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
    assert_unique_flush_in_room,
)
from app.utils import validation_error_response

bp = Blueprint("flush_harvests", __name__, url_prefix="/api/flush-harvests")

create_schema = FlushHarvestCreateSchema()
out_schema = FlushHarvestOutSchema()
out_many = FlushHarvestOutSchema(many=True)


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
        assert_unique_flush_in_room(rows)
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
            existing.harvested_at = data["harvested_at"]
            existing.weight_kg = data["weight_kg"]
            existing.grade = data["grade"]
            existing.operator_name = data["operator_name"]
            try:
                db.commit()
            except IntegrityError:
                return jsonify({"detail": "潮次号冲突"}), 409
            db.refresh(existing)
            return jsonify(out_schema.dump(existing)), 201
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
            return jsonify({"detail": "潮次号冲突"}), 409
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
        item.room_id = data["room_id"]
        item.harvested_at = data["harvested_at"]
        item.flush_no = data["flush_no"]
        item.weight_kg = data["weight_kg"]
        item.grade = data["grade"]
        item.operator_name = data["operator_name"]
        try:
            db.commit()
        except IntegrityError:
            return jsonify({"detail": "潮次号冲突"}), 409
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
