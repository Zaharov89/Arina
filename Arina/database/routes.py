from flask import Blueprint, jsonify

from Arina.database.config import DATABASE_URL, is_database_configured

database_bp = Blueprint("database", __name__, url_prefix="/database")


@database_bp.route("/status")
def database_status():
    return jsonify(
        {
            "status": "configured" if is_database_configured() else "planned",
            "module": "database",
            "postgresql_configured": is_database_configured(),
            "database_url_present": bool(DATABASE_URL),
            "message": "PostgreSQL будет подключён на следующем архитектурном этапе.",
        }
    )
