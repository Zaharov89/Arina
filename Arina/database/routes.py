from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from Arina.database.config import DATABASE_URL, get_masked_database_url, is_database_configured
from Arina.database.repositories import ReferenceDataRepository
from Arina.database.session import get_session_factory, ping_database


database_bp = Blueprint("database", __name__, url_prefix="/database")


def get_reference_repository() -> ReferenceDataRepository:
    session_factory = get_session_factory()
    session = session_factory()
    return ReferenceDataRepository(session)


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


@database_bp.route("/subjects")
def subjects_api():
    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            subjects = ReferenceDataRepository(session).get_subjects()

        return jsonify({"status": "ok", "data": subjects})
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify({"status": "error", "message": "Не удалось получить список предметов.", "error": str(error)}), 500


@database_bp.route("/school-classes")
def school_classes_api():
    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            classes = ReferenceDataRepository(session).get_school_classes()

        return jsonify({"status": "ok", "data": classes})
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify({"status": "error", "message": "Не удалось получить список классов.", "error": str(error)}), 500


@database_bp.route("/topics")
def topics_api():
    subject_code = request.args.get("subject_code") or None
    raw_class_number = request.args.get("class_number")
    class_number = None

    if raw_class_number:
        try:
            class_number = int(raw_class_number)
        except ValueError:
            return jsonify({"status": "validation_error", "message": "class_number должен быть числом."}), 400

    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            topics = ReferenceDataRepository(session).get_topics(subject_code=subject_code, class_number=class_number)

        return jsonify({"status": "ok", "data": topics})
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify({"status": "error", "message": "Не удалось получить список тем.", "error": str(error)}), 500
