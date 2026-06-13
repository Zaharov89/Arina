import os

from flask import Flask

from Arina.backend.routes.english import english_bp
from Arina.backend.routes.math import math_bp
from Arina.backend.routes.pages import pages_bp
from Arina.backend.routes.results import results_bp
from Arina.backend.routes.russian import russian_bp
from Arina.backend.routes.vocabulary_api import vocabulary_api_bp
from Arina.auth.routes import auth_bp
from Arina.config import FLASK_HOST, FLASK_PORT
from Arina.database.routes import database_bp
from Arina.stats.routes import stats_bp


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder=TEMPLATE_DIR,
        static_folder=STATIC_DIR,
    )

    register_blueprints(app)
    return app


def register_blueprints(app: Flask) -> None:
    """Register all application blueprints in one place."""
    app.register_blueprint(pages_bp)
    app.register_blueprint(english_bp)
    app.register_blueprint(russian_bp)
    app.register_blueprint(math_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(vocabulary_api_bp)
    app.register_blueprint(stats_bp)

    # Future architecture sections. They are registered now so URLs are ready,
    # but real implementation will be added later.
    app.register_blueprint(auth_bp)
    app.register_blueprint(database_bp)

    print(f"✅ Flask blueprints registered: {', '.join(app.blueprints.keys())}")


def get_run_config() -> tuple[str, int]:
    """Return host and port for local launch."""
    return FLASK_HOST, FLASK_PORT
