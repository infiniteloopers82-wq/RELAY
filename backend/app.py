import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, migrate

load_dotenv()


def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    from routes.auth import bp as auth_bp
    from routes.resources import bp as resources_bp
    from routes.bookings import bp as bookings_bp
    from routes.incidents import bp as incidents_bp
    from routes.dashboard import bp as dashboard_bp
    from routes.audit import bp as audit_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(incidents_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(audit_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "RELAY API"}), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found", "code": "not_found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return jsonify({"error": "Internal server error", "code": "server_error"}), 500

    with app.app_context():
        from models import User, Resource, Booking, ConditionReport, Incident, AuditLog
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "true").lower() == "true",
    )
