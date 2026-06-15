import os

from flask import Flask, request

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
from Arina.stats.routes import stats_bp


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
AUTH_STATE_SCRIPT = '<script src="/static/js/auth-state.js" defer></script>'


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder=TEMPLATE_DIR,
        static_folder=STATIC_DIR,
    )

    register_blueprints(app)
    register_auth_script_injector(app)
    return app


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints in one place."""
    app.register_blueprint(pages_bp)
    app.register_blueprint(english_bp)
    app.register_blueprint(russian_bp)
    app.register_blueprint(math_bp)
    app.register_blueprint(world_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(vocabulary_api_bp)
    app.register_blueprint(stats_bp)

    # Future architecture sections. They are registered now so URLs are ready,
    # but real implementation will be added later.
    app.register_blueprint(auth_bp)
    app.register_blueprint(auth_me_bp)
    app.register_blueprint(database_bp)

    print(f"✅ Flask blueprints registered: {', '.join(app.blueprints.keys())}")


def register_auth_script_injector(app: Flask) -> None:
    """Inject frontend auth guard into application HTML pages."""

    @app.after_request
    def inject_auth_state_script(response):
        if not should_inject_auth_script(response):
            return response

        body = response.get_data(as_text=True)
        if AUTH_STATE_SCRIPT in body:
            return response

        if "</body>" in body:
            body = body.replace("</body>", f"    {AUTH_STATE_SCRIPT}\n</body>", 1)
            response.set_data(body)
            response.headers["Content-Length"] = str(len(response.get_data()))

        return response


def should_inject_auth_script(response) -> bool:
    """Return True for protected HTML pages where frontend auth guard is needed."""
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
    return FLASK_HOST, FLASK_PORT
