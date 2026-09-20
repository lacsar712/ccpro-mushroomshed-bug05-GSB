from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models.flush_harvest import FlushHarvest
from app.models.room import Room
from app.schemas.flush_harvest import (
    FlushHarvestCreateSchema,
    FlushHarvestOutSchema,
)
from app.utils import validation_error_response

bp = Blueprint("flush_harvests", __name__, url_prefix="/api/flush-harvests")

create_schema = FlushHarvestCreateSchema()
out_schema = FlushHarvestOutSchema()
out_many = FlushHarvestOutSchema(many=True)

DUPLICATE_DETAIL = "同一出菇房内潮次序号 {flush_no} 已存在，潮次序号不可重复"


def _duplicate_exists(db, room_id: int, flush_no: int, exclude_id: int | None = None) -> bool:
    q = db.query(FlushHarvest.id).filter(
        FlushHarvest.room_id == room_id,
        FlushHarvest.flush_no == flush_no,
    )
    if exclude_id is not None:
        q = q.filter(FlushHarvest.id != exclude_id)
    return db.query(q.exists()).scalar()


@bp.get("")
@jwt_required()
def list_flush_harvests():
    db = SessionLocal()
    try:
        room_id = request.args.get("roomId", type=int)
        q = db.query(FlushHarvest)
        if room_id is not None:
            q = q.filter(FlushHarvest.room_id == room_id)
        rows = q.order_by(FlushHarvest.harvested_at.desc()).all()
        # 历史数据即便存在叠号，清单也必须照常返回，不做唯一性断言
        return jsonify(out_many.dump(rows))
    finally:
        db.close()


@bp.post("")
@jwt_required()
def create_flush_harvest():
    db = SessionLocal()
    try:
        try:
            data = create_schema.load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return validation_error_response(err)
        room = db.query(Room).filter(Room.id == data["room_id"]).first()
        if not room:
            return jsonify({"detail": "出菇室不存在"}), 400
        # 先查后插：绝大多数重复请求在这里被挡下，旧记录绝不被改写
        if _duplicate_exists(db, data["room_id"], data["flush_no"]):
            return (
                jsonify({"detail": DUPLICATE_DETAIL.format(flush_no=data["flush_no"])}),
                409,
            )
        item = FlushHarvest(
            room_id=data["room_id"],
            harvested_at=data["harvested_at"],
            flush_no=data["flush_no"],
            weight_kg=data["weight_kg"],
            grade=data["grade"],
            operator_name=data["operator_name"],
        )
        db.add(item)
        try:
            db.commit()
        except IntegrityError:
            # 两路并发同序号时由数据库唯一约束兜底：本事务必须回滚，
            # 否则脏连接会污染后续请求。
            db.rollback()
            if _duplicate_exists(db, data["room_id"], data["flush_no"]):
                return (
                    jsonify({"detail": DUPLICATE_DETAIL.format(flush_no=data["flush_no"])}),
                    409,
                )
            raise
        db.refresh(item)
        return jsonify(out_schema.dump(item)), 201
    finally:
        db.close()


@bp.put("/<int:harvest_id>")
@jwt_required()
def update_flush_harvest(harvest_id: int):
    db = SessionLocal()
    try:
        try:
            data = create_schema.load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return validation_error_response(err)
        item = db.query(FlushHarvest).filter(FlushHarvest.id == harvest_id).first()
        if not item:
            return jsonify({"detail": "采收记录不存在"}), 404
        room = db.query(Room).filter(Room.id == data["room_id"]).first()
        if not room:
            return jsonify({"detail": "出菇室不存在"}), 400
        # 改去占别的记录的序号（含换房后撞上目标房已有序号）一律拒绝
        if _duplicate_exists(db, data["room_id"], data["flush_no"], exclude_id=item.id):
            return (
                jsonify({"detail": DUPLICATE_DETAIL.format(flush_no=data["flush_no"])}),
                409,
            )
        item.room_id = data["room_id"]
        item.harvested_at = data["harvested_at"]
        item.flush_no = data["flush_no"]
        item.weight_kg = data["weight_kg"]
        item.grade = data["grade"]
        item.operator_name = data["operator_name"]
        try:
            db.commit()
        except IntegrityError:
            # 并发改号撞车时唯一约束兜底，回滚后给出明确原因
            db.rollback()
            if _duplicate_exists(db, data["room_id"], data["flush_no"], exclude_id=harvest_id):
                return (
                    jsonify({"detail": DUPLICATE_DETAIL.format(flush_no=data["flush_no"])}),
                    409,
                )
            raise
        db.refresh(item)
        return jsonify(out_schema.dump(item))
    finally:
        db.close()


@bp.delete("/<int:harvest_id>")
@jwt_required()
def delete_flush_harvest(harvest_id: int):
    db = SessionLocal()
    try:
        item = db.query(FlushHarvest).filter(FlushHarvest.id == harvest_id).first()
        if not item:
            return jsonify({"detail": "采收记录不存在"}), 404
        db.delete(item)
        db.commit()
        return "", 204
    finally:
        db.close()
