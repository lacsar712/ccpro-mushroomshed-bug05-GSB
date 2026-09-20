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

CONFLICT_DETAIL = "同一间出菇房内潮次序号不可重复"


@bp.get("")
@jwt_required()
def list_flush_harvests():
    db = SessionLocal()
    try:
        room_id = request.args.get("roomId", type=int)
        q = db.query(FlushHarvest)
        if room_id is not None:
            q = q.filter(FlushHarvest.room_id == room_id)
        # 即便历史数据中存在叠号也必须能正常列出，不能因此报错
        rows = q.order_by(FlushHarvest.harvested_at.desc()).all()
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
        existing = (
            db.query(FlushHarvest)
            .filter(
                FlushHarvest.room_id == data["room_id"],
                FlushHarvest.flush_no == data["flush_no"],
            )
            .first()
        )
        if existing:
            # 序号已存在：拒绝新增，绝不覆盖旧记录的重量/等级
            return (
                jsonify(
                    {
                        "detail": (
                            f"{CONFLICT_DETAIL}：该出菇房已记录潮次 "
                            f"{data['flush_no']}（记录 #{existing.id}），请勿重复登记"
                        )
                    }
                ),
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
            # 两路并发登记同一潮次：唯一约束兜底，只留先提交的一笔
            db.rollback()
            return (
                jsonify(
                    {
                        "detail": (
                            f"{CONFLICT_DETAIL}：潮次 {data['flush_no']} 刚被另一笔登记占用，"
                            "请刷新后重试"
                        )
                    }
                ),
                409,
            )
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
        occupant = (
            db.query(FlushHarvest)
            .filter(
                FlushHarvest.room_id == data["room_id"],
                FlushHarvest.flush_no == data["flush_no"],
                FlushHarvest.id != harvest_id,
            )
            .first()
        )
        if occupant:
            # 改序号/改房间会撞到别人的序号：拒绝，不能叠号
            return (
                jsonify(
                    {
                        "detail": (
                            f"{CONFLICT_DETAIL}：潮次 {data['flush_no']} 已被记录 "
                            f"#{occupant.id} 占用，无法改到该序号"
                        )
                    }
                ),
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
            # 并发改序号撞上的兜底：回滚，保持原记录不变
            db.rollback()
            return (
                jsonify(
                    {
                        "detail": (
                            f"{CONFLICT_DETAIL}：潮次 {data['flush_no']} 已被其他记录占用，"
                            "请刷新后重试"
                        )
                    }
                ),
                409,
            )
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
        # 物理删除：删掉后该 (room_id, flush_no) 序号即可重新使用
        db.commit()
        return "", 204
    finally:
        db.close()
