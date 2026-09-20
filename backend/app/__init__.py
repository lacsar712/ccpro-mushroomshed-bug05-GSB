from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.config import settings
from app.migrations import ensure_flush_unique_index
from app.routes import auth, climate_logs, dashboard, flush_harvests, rooms, sheds


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = settings.jwt_secret
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.jwt_access_token_expires

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    JWTManager(app)

    # 旧库没有唯一索引，启动时补建（含历史叠号去重）；幂等
    ensure_flush_unique_index()

    app.register_blueprint(auth.bp)
    app.register_blueprint(sheds.bp)
    app.register_blueprint(rooms.bp)
    app.register_blueprint(climate_logs.bp)
    app.register_blueprint(flush_harvests.bp)
    app.register_blueprint(dashboard.bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "MushroomShed"})

    return app
