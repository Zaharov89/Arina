import random

from flask import Blueprint, render_template, request

from Arina.backend.routes.common import get_int_arg, get_student
from Arina.russian_language.class_2 import russianQuestions as questions2
from Arina.russian_language.class_3 import russianQuestions as questions3

russian_bp = Blueprint("russian", __name__)


@russian_bp.route("/russian")
def russian_menu():
    student = get_student()
    class2_words = list(questions2.keys())
    class3_words = list(questions3.keys())
    class1_words = []

    return render_template(
        "russian/menu.html",
        class1_words=class1_words,
        class2_words=class2_words,
        class3_words=class3_words,
        student=student,
    )


@russian_bp.route("/russian/rules")
def russian_rules():
    student = get_student()
    class2_words = list(questions2.keys())
    class3_words = list(questions3.keys())
    class1_words = []

    return render_template(
        "russian/rules.html",
        class1_words=class1_words,
        class2_words=class2_words,
        class3_words=class3_words,
        student=student,
    )


@russian_bp.route("/russian/test_setup")
def russian_test_setup():
    student = get_student()
    class2_words = list(questions2.keys())
    class3_words = list(questions3.keys())
    class1_words = []

    return render_template(
        "russian/test_setup.html",
        class1_words=class1_words,
        class2_words=class2_words,
        class3_words=class3_words,
        student=student,
    )


@russian_bp.route("/russian/test")
def russian_test():
    student = get_student()
    class_num = request.args.get("class", "all")
    total_requested = get_int_arg("words", default=25, min_value=1, max_value=200)

    if class_num == "2":
        all_available = list(questions2.keys())
    elif class_num == "3":
        all_available = list(questions3.keys())
    else:
        all_available = list(set(list(questions2.keys()) + list(questions3.keys())))

    if not all_available:
        test_words = []
    elif len(all_available) >= total_requested:
        test_words = random.sample(all_available, total_requested)
    else:
        test_words = random.choices(all_available, k=total_requested)

    return render_template(
        "russian/test.html",
        test_words=test_words,
        total_words=total_requested,
        student=student,
    )
