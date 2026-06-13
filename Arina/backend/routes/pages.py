from flask import Blueprint, render_template

from Arina.backend.routes.common import get_student

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def home():
    return render_template("index.html")


@pages_bp.route("/subjects")
def subjects_menu():
    return render_template("subjects.html", student=get_student())


@pages_bp.route("/student_selection")
def student_selection():
    return render_template("student_selection/index.html")
