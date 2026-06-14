from flask import Blueprint, jsonify
from sqlalchemy.exc import SQLAlchemyError

from Arina.database.config import DATABASE_URL, get_masked_database_url, is_database_configured
from Arina.database.repositories import ReferenceDataRepository
from Arina.database.session import get_session_factory, ping_database


database_bp = Blueprint("database", __name__, url_prefix="/database")


@database_bp.route("/status")
def database_status():
    if not is_database_configured():
        return jsonify(
            {
                "status": "not_configured",
                "module": "database",
                "postgresql_configured": False,
                "database_url_present": bool(DATABASE_URL),
                "message": "ARINA_DATABASE_URL не задан. Создайте .env по примеру .env.example.",
            }
        )

    try:
        ping_database()

        session_factory = get_session_factory()
        with session_factory() as session:
            summary = ReferenceDataRepository(session).get_summary()

        return jsonify(
            {
                "status": "connected",
                "module": "database",
                "postgresql_configured": True,
                "database_url_present": True,
                "database_url": get_masked_database_url(),
                "reference_data": summary,
                "message": "PostgreSQL подключён и отвечает.",
            }
        )
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify(
            {
                "status": "error",
                "module": "database",
                "postgresql_configured": True,
                "database_url_present": True,
                "database_url": get_masked_database_url(),
                "error": str(error),
                "message": "Не удалось подключиться к PostgreSQL. Проверьте .env, пароль, порт и что сервер запущен.",
            }
        ), 500
