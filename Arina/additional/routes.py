from flask import Blueprint, render_template

from Arina.backend.routes.common import get_student

additional_bp = Blueprint("additional", __name__)


@additional_bp.route("/additional")
def additional_index():
    """Show non-school additional learning programs."""
    return render_template("additional/index.html", student=get_student())
