import logging
import os
import time

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from Arina.backend.routes.english import english_bp
from Arina.backend.routes.math import math_bp
from Arina.backend.routes.pages import pages_bp
from Arina.backend.routes.results import results_bp
from Arina.backend.routes.russian import russian_bp
from Arina.backend.routes.vocabulary_api import vocabulary_api_bp
from Arina.backend.routes.world import world_bp
from Arina.auth.me_routes import auth_me_bp
from Arina.auth.routes import auth_bp
from Arina.config import FLASK_HOST, FLASK_PORT
from Arina.database.routes import database_bp
from Arina.logging_config import configure_logging
from Arina.stats.routes import stats_bp

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
AUTH_STATE_SCRIPT = '<script src="/static/js/auth-state.js" defer></script>'


def create_app() -> Flask:
    """Create and configure the Flask application."""
    configure_logging()
    app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
    register_request_logging(app)
    register_error_handlers(app)
    register_blueprints(app)
    register_auth_script_injector(app)
    logger.info("Flask app created: template_dir=%s static_dir=%s", TEMPLATE_DIR, STATIC_DIR)
    return app


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints in one place."""
    blueprints = [pages_bp, english_bp, russian_bp, math_bp, world_bp, results_bp, vocabulary_api_bp, stats_bp, auth_bp, auth_me_bp, database_bp]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    logger.info("Flask blueprints registered: %s", ", ".join(app.blueprints.keys()))


def register_request_logging(app: Flask) -> None:
    @app.before_request
    def log_request_start():
        request._arina_start_time = time.monotonic()
        logger.info("HTTP request started: method=%s path=%s remote=%s", request.method, request.path, request.remote_addr)

    @app.after_request
    def log_request_finish(response):
        started_at = getattr(request, "_arina_start_time", None)
        duration_ms = round((time.monotonic() - started_at) * 1000, 2) if started_at else None
        logger.info("HTTP request finished: method=%s path=%s status=%s duration_ms=%s", request.method, request.path, response.status_code, duration_ms)
        return response


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        logger.warning("HTTP error: status=%s path=%s message=%s", error.code, request.path, error.description)
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"error": error.name, "message": error.description}), error.code
        return error

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error: Exception):
        logger.exception("Unhandled application error: method=%s path=%s", request.method, request.path)
        if request.path.startswith("/api/") or request.is_json:
            return jsonify({"error": "internal_server_error", "message": "Внутренняя ошибка приложения. Подробности записаны в лог."}), 500
        raise error


def register_auth_script_injector(app: Flask) -> None:
    """Inject frontend auth guard into application HTML pages."""

    @app.after_request
    def inject_auth_state_script(response):
        if not should_inject_frontend_scripts(response):
            return response
        body = response.get_data(as_text=True)
        if AUTH_STATE_SCRIPT not in body and "</body>" in body:
            body = body.replace("</body>", f"    {AUTH_STATE_SCRIPT}\n</body>", 1)
            response.set_data(body)
            response.headers["Content-Length"] = str(len(response.get_data()))
        return response


def should_inject_frontend_scripts(response) -> bool:
    """Return True for protected HTML pages where frontend scripts are needed."""
    if request.path.startswith("/static/"):
        return False
    if request.path.startswith("/auth/"):
        return False
    if request.path.startswith("/database/"):
        return False
    if request.path.startswith("/api/"):
        return False
    content_type = response.headers.get("Content-Type", "")
    return response.status_code == 200 and "text/html" in content_type


def get_run_config() -> tuple[str, int]:
    """Return host and port for local launch."""
    logger.info("Run config loaded: host=%s port=%s", FLASK_HOST, FLASK_PORT)
    return FLASK_HOST, FLASK_PORT
