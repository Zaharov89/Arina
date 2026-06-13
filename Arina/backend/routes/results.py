from flask import Blueprint, render_template

from Arina.backend.routes.common import get_student

results_bp = Blueprint("results", __name__)


@results_bp.route("/results/english")
def results_english():
    return render_template("results/english/results.html", student=get_student())


@results_bp.route("/results/russian")
def results_russian():
    return render_template("results/russian/results.html", student=get_student())


@results_bp.route("/results/math")
def results_math():
    return render_template("results/math/results.html", student=get_student())


@results_bp.route("/results/world")
def results_world():
    return render_template("results/world/results.html", student=get_student())
