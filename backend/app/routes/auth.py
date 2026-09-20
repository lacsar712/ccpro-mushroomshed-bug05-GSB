from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from marshmallow import ValidationError

from app.auth import verify_password
from app.database import SessionLocal
from app.models.user import User
from app.schemas.auth import JsonLoginSchema, LoginResponseSchema, UserOutSchema
from app.utils import validation_error_response

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

login_schema = JsonLoginSchema()
user_out = UserOutSchema()
login_out = LoginResponseSchema()


@bp.post("/login")
def login():
    db = SessionLocal()
    try:
        if request.content_type and "application/json" in request.content_type:
            try:
                data = login_schema.load(request.get_json(silent=True) or {})
            except ValidationError as err:
                return validation_error_response(err)
            username = data["username"]
            password = data["password"]
        else:
            username = request.form.get("username")
            password = request.form.get("password")
            if not username or not password:
                return jsonify({"detail": "用户名与密码必填"}), 400

        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            return jsonify({"detail": "用户名或密码错误"}), 401

        token = create_access_token(identity=user.username)
        payload = {
            "access_token": token,
            "token_type": "bearer",
            "user": user_out.dump(user),
        }
        return jsonify(payload)
    finally:
        db.close()


@bp.get("/me")
@jwt_required()
def me():
    db = SessionLocal()
    try:
        username = get_jwt_identity()
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return jsonify({"detail": "无效或过期的令牌"}), 401
        return jsonify(user_out.dump(user))
    finally:
        db.close()
