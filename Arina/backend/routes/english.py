import random

from flask import Blueprint, abort, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from Arina.backend.routes.common import get_int_arg, get_student
from Arina.database.session import get_session_factory
from Arina.english_language.vocabulary import get_english_vocabulary_words

english_bp = Blueprint("english", __name__)

SUPPORTED_ENGLISH_CLASSES = list(range(1, 12))
IMPLEMENTED_TEST_CLASSES = {2, 3}
IMPLEMENTED_LEARNING_CLASSES = set()


def get_english_words_for_class(class_num: str) -> list[dict]:
    class_number = None if class_num == "all" else int(class_num)
    session_factory = get_session_factory()
    with session_factory() as session:
        return get_english_vocabulary_words(session, class_number)


def get_english_class_words() -> tuple[list[dict], list[dict]]:
    return get_english_words_for_class("2"), get_english_words_for_class("3")


@english_bp.route("/english/menu")
def english_menu():
    student = get_student()
    return render_template("english/menu.html", classes=SUPPORTED_ENGLISH_CLASSES, implemented_test_classes=IMPLEMENTED_TEST_CLASSES, implemented_learning_classes=IMPLEMENTED_LEARNING_CLASSES, student=student)


@english_bp.route("/english/class/<int:class_num>")
def english_class_page(class_num: int):
    if class_num not in SUPPORTED_ENGLISH_CLASSES:
        abort(404)
    return render_template("english/class_page.html", student=get_student(), class_num=class_num, is_first_class=class_num == 1, is_testing_implemented=class_num in IMPLEMENTED_TEST_CLASSES)


@english_bp.route("/english/vocabulary")
def english_vocabulary():
    student = get_student()
    try:
        class2_words, class3_words = get_english_class_words()
        error_message = None
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        class2_words, class3_words = [], []
        error_message = f"Не удалось получить английский словарь из БД: {error}"
    return render_template("english/vocabulary.html", class2_words=class2_words, class3_words=class3_words, student=student, error_message=error_message)


@english_bp.route("/english/rules")
def english_rules():
    student = get_student()
    try:
        class2_words, class3_words = get_english_class_words()
    except (RuntimeError, SQLAlchemyError, OSError):
        class2_words, class3_words = [], []
    return render_template("english/rules.html", class2_words=class2_words, class3_words=class3_words, student=student)


@english_bp.route("/english/test_setup")
def english_test_setup():
    student = get_student()
    try:
        class2_words, class3_words = get_english_class_words()
        error_message = None
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        class2_words, class3_words = [], []
        error_message = f"Не удалось получить английский словарь из БД: {error}"
    return render_template("english/test_setup.html", class2_words=class2_words, class3_words=class3_words, student=student, error_message=error_message)


@english_bp.route("/english/test")
def english_test():
    student = get_student()
    class_num = request.args.get("class", "all")
    test_type = request.args.get("type", "en_to_ru")
    total_requested = get_int_arg("words", default=25, min_value=1, max_value=200)

    if class_num not in {"2", "3", "all"}:
        class_num = "all"

    try:
        all_available = get_english_words_for_class(class_num)
        class2_words, class3_words = get_english_class_words()
        error_message = None
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        all_available = []
        class2_words, class3_words = [], []
        error_message = f"Не удалось получить английский словарь из БД: {error}"

    if not all_available:
        test_words = []
    elif len(all_available) >= total_requested:
        test_words = random.sample(all_available, total_requested)
    else:
        test_words = random.choices(all_available, k=total_requested)

    return render_template("english/test.html", class2_words=class2_words, class3_words=class3_words, test_words=test_words, total_words=total_requested, test_type=test_type, student=student, error_message=error_message)
