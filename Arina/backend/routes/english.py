import random

from flask import Blueprint, render_template, request

from Arina.backend.routes.common import get_int_arg, get_student
from Arina.english_language.class_2 import class2Words
from Arina.english_language.class_3 import class3Words

english_bp = Blueprint("english", __name__)


@english_bp.route("/english/menu")
def english_menu():
    student = get_student()
    return render_template(
        "english/menu.html",
        class2_words=class2Words,
        class3_words=class3Words,
        student=student,
    )


@english_bp.route("/english/vocabulary")
def english_vocabulary():
    student = get_student()
    return render_template(
        "english/vocabulary.html",
        class2_words=class2Words,
        class3_words=class3Words,
        student=student,
    )


@english_bp.route("/english/rules")
def english_rules():
    student = get_student()
    return render_template(
        "english/rules.html",
        class2_words=class2Words,
        class3_words=class3Words,
        student=student,
    )


@english_bp.route("/english/test_setup")
def english_test_setup():
    student = get_student()
    return render_template(
        "english/test_setup.html",
        class2_words=class2Words,
        class3_words=class3Words,
        student=student,
    )


@english_bp.route("/english/test")
def english_test():
    student = get_student()
    class_num = request.args.get("class", "all")
    test_type = request.args.get("type", "en_to_ru")
    total_requested = get_int_arg("words", default=25, min_value=1, max_value=200)

    if class_num == "all":
        all_available = class2Words + class3Words
    elif class_num == "2":
        all_available = class2Words
    elif class_num == "3":
        all_available = class3Words
    else:
        all_available = class2Words + class3Words

    if not all_available:
        test_words = []
    elif len(all_available) >= total_requested:
        test_words = random.sample(all_available, total_requested)
    else:
        test_words = random.choices(all_available, k=total_requested)

    return render_template(
        "english/test.html",
        class2_words=class2Words,
        class3_words=class3Words,
        test_words=test_words,
        total_words=total_requested,
        test_type=test_type,
        student=student,
    )
