import logging

from flask import Blueprint, jsonify, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from Arina.auth.services import AuthTokenError
from Arina.stats.schemas import StatsValidationError
from Arina.stats.services import get_diary_stats, save_test_attempt

stats_bp = Blueprint("stats", __name__)
logger = logging.getLogger(__name__)


def get_access_token_from_request() -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return ""


@stats_bp.route("/stats")
@stats_bp.route("/diary")
def stats_page():
    logger.info("Diary page opened")
    return render_template("diary/diary.html")


@stats_bp.route("/api/stats")
def api_get_stats():
    try:
        logger.info("API stats requested")
        return jsonify(get_diary_stats(get_access_token_from_request()))
    except AuthTokenError as error:
        logger.warning("API stats auth error: %s", error)
        return jsonify({"error": str(error), "status": "unauthorized"}), 401
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        logger.exception("API stats PostgreSQL read failed")
        return jsonify({"error": f"Ошибка чтения дневника из PostgreSQL: {error}"}), 500


@stats_bp.route("/api/test-attempts", methods=["POST"])
def api_save_test_attempt():
    try:
        logger.info("API save test attempt requested")
        data, status_code = save_test_attempt(get_access_token_from_request(), request.get_json(silent=True))
        return jsonify(data), status_code
    except StatsValidationError as error:
        logger.warning("API save test attempt validation error: %s", error)
        return jsonify({"status": "validation_error", "message": str(error)}), 400
    except AuthTokenError as error:
        logger.warning("API save test attempt auth error: %s", error)
        return jsonify({"status": "unauthorized", "message": str(error)}), 401
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        logger.exception("API save test attempt PostgreSQL write failed")
        return jsonify({"status": "error", "message": f"Не удалось сохранить результат в PostgreSQL: {error}"}), 500
