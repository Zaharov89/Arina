from flask import Blueprint, render_template
from sqlalchemy.exc import SQLAlchemyError

from Arina.backend.routes.common import get_student
from Arina.database.repositories import ReferenceDataRepository
from Arina.database.session import get_session_factory


pages_bp = Blueprint("pages", __name__)


SUBJECT_ROUTE_MAP = {
    "math": "/math",
    "russian": "/russian",
    "world": "/world",
    "english": "/english/menu",
}

FALLBACK_SUBJECTS = [
    {"code": "math", "title": "Математика"},
    {"code": "russian", "title": "Русский язык"},
    {"code": "world", "title": "Окружающий мир"},
    {"code": "english", "title": "Английский язык"},
]


def get_subjects_for_menu() -> list[dict]:
    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            subjects = ReferenceDataRepository(session).get_subjects()
    except (RuntimeError, SQLAlchemyError, OSError):
        subjects = FALLBACK_SUBJECTS

    menu_subjects = []
    for subject in subjects:
        code = subject.get("code")
        route = SUBJECT_ROUTE_MAP.get(code)
        if not route:
            continue
        menu_subjects.append({"code": code, "title": subject.get("title", code), "route": route})

    return menu_subjects or [
        {"code": subject["code"], "title": subject["title"], "route": SUBJECT_ROUTE_MAP[subject["code"]]}
        for subject in FALLBACK_SUBJECTS
    ]


@pages_bp.route("/")
def home():
    return render_template("index.html")


@pages_bp.route("/subjects")
def subjects_menu():
    return render_template("subjects.html", student=get_student(), subjects=get_subjects_for_menu())


@pages_bp.route("/student_selection")
def student_selection():
    return render_template("student_selection/index.html")
