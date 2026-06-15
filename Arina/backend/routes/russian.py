import random
from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from Arina.backend.routes.common import get_int_arg, get_json_body, get_student
from Arina.backend.services.catalog import build_topic_options, get_topic_or_none, merge_db_topics_with_content
from Arina.database.session import get_session_factory
from Arina.russian_language.class_1_tasks import generate_russian_class_1_topic_task, normalize_text
from Arina.russian_language.class_1_topics import RUSSIAN_CLASS_1_TOPICS
from Arina.russian_language.class_2_tasks import generate_russian_class_2_topic_task
from Arina.russian_language.class_2_topics import RUSSIAN_CLASS_2_TOPICS
from Arina.russian_language.class_3_tasks import generate_russian_class_3_topic_task
from Arina.russian_language.class_3_topics import RUSSIAN_CLASS_3_TOPICS
from Arina.russian_language.vocabulary import get_russian_vocabulary_word_list, get_russian_vocabulary_words

russian_bp = Blueprint("russian", __name__)

SUPPORTED_RUSSIAN_CLASSES = list(range(1, 12))
IMPLEMENTED_TEST_CLASSES = {1, 2, 3}
IMPLEMENTED_LEARNING_CLASSES = {1, 2, 3}
CONTROL_SLICE_TYPE = "control_slice"
control_topic_cursor = 0
TOPICS_BY_CLASS = {1: RUSSIAN_CLASS_1_TOPICS, 2: RUSSIAN_CLASS_2_TOPICS, 3: RUSSIAN_CLASS_3_TOPICS}
DEFAULT_TOPIC_BY_CLASS = {1: "sounds_and_letters", 2: "sounds_letters_review", 3: "word_structure"}
VOCABULARY_TOPIC_CODES = {"mini_dictations", "vocabulary_words_2", "vocabulary_words_3"}


def get_russian_topics(class_num: int) -> dict:
    return merge_db_topics_with_content("russian", class_num, TOPICS_BY_CLASS.get(class_num, RUSSIAN_CLASS_1_TOPICS))


def get_russian_topic_from_catalog(class_num: int, topic_id: str) -> dict | None:
    return get_topic_or_none("russian", class_num, topic_id, TOPICS_BY_CLASS.get(class_num, RUSSIAN_CLASS_1_TOPICS))


def get_next_control_topic_id(class_num: int) -> str:
    global control_topic_cursor
    topic_ids = [topic_id for topic_id in get_russian_topics(class_num).keys() if topic_id not in VOCABULARY_TOPIC_CODES]
    if not topic_ids:
        return DEFAULT_TOPIC_BY_CLASS.get(class_num, "sounds_and_letters")
    topic_id = topic_ids[control_topic_cursor % len(topic_ids)]
    control_topic_cursor += 1
    return topic_id


def get_russian_vocabulary_words_for_class(class_num: str) -> list[str]:
    class_number = None if class_num == "all" else int(class_num)
    session_factory = get_session_factory()
    with session_factory() as session:
        return get_russian_vocabulary_word_list(session, class_number)


def get_russian_vocabulary_words_for_test(class_num: str) -> list[str]:
    class_number = None if class_num == "all" else int(class_num)
    session_factory = get_session_factory()
    with session_factory() as session:
        if class_number in {1, 2, 3}:
            words = []
            for current_class in range(1, class_number + 1):
                words.extend(get_russian_vocabulary_word_list(session, current_class))
            return list(dict.fromkeys(words))
        return get_russian_vocabulary_word_list(session, None)


def get_russian_vocabulary_items_for_class(class_num: int) -> list[dict]:
    session_factory = get_session_factory()
    with session_factory() as session:
        return get_russian_vocabulary_words(session, class_num)


def normalize_used_questions(raw_used_questions: Any) -> list[str]:
    if not isinstance(raw_used_questions, list):
        return []
    return [str(question).strip() for question in raw_used_questions if str(question).strip()][-300:]


def normalize_class_num(raw_class: Any, default: int = 1) -> int:
    try:
        class_num = int(raw_class)
    except (TypeError, ValueError):
        return default
    return class_num if class_num in (1, 2, 3) else default


def build_task_key(task: dict) -> str:
    question = str(task.get("question", "")).strip()
    choices = task.get("choices") or []
    if choices:
        return question + " | " + " | ".join(map(str, choices))
    return question


def ensure_unique_task(task: dict, used_questions: list[str]) -> dict:
    task_key = build_task_key(task)
    if task_key in used_questions:
        task_key = f"{task_key} | repeat-{len(used_questions) + 1}"
    task["question_key"] = task_key
    task["is_repeat"] = False
    return task


@russian_bp.route("/russian")
def russian_menu():
    return render_template("russian/menu.html", classes=SUPPORTED_RUSSIAN_CLASSES, implemented_test_classes=IMPLEMENTED_TEST_CLASSES, implemented_learning_classes=IMPLEMENTED_LEARNING_CLASSES, student=get_student())


@russian_bp.route("/russian/class/<int:class_num>")
def russian_class_page(class_num: int):
    if class_num not in SUPPORTED_RUSSIAN_CLASSES:
        abort(404)
    if class_num in IMPLEMENTED_LEARNING_CLASSES:
        return render_template("russian/learning.html", student=get_student(), topics=get_russian_topics(class_num), class_num=class_num, from_class_page=True, vocabulary_topic_codes=VOCABULARY_TOPIC_CODES)
    return render_template("russian/class_page.html", student=get_student(), class_num=class_num, is_learning_implemented=False, is_testing_implemented=class_num in IMPLEMENTED_TEST_CLASSES)


@russian_bp.route("/russian/learning")
def russian_learning():
    class_num = get_int_arg("class", default=1, min_value=1, max_value=11)
    if class_num not in IMPLEMENTED_LEARNING_CLASSES:
        return render_template("russian/class_page.html", student=get_student(), class_num=class_num, is_learning_implemented=False, is_testing_implemented=class_num in IMPLEMENTED_TEST_CLASSES)
    return render_template("russian/learning.html", student=get_student(), topics=get_russian_topics(class_num), class_num=class_num, from_class_page=False, vocabulary_topic_codes=VOCABULARY_TOPIC_CODES)


@russian_bp.route("/russian/learning/topic/<topic_id>")
def russian_learning_topic(topic_id: str):
    class_num = get_int_arg("class", default=1, min_value=1, max_value=11)
    if topic_id in VOCABULARY_TOPIC_CODES:
        return render_template("russian/vocabulary_menu.html", student=get_student(), class_num=class_num)
    topic = get_russian_topic_from_catalog(class_num, topic_id)
    if not topic:
        abort(404)
    return render_template("russian/learning_topic.html", student=get_student(), topic_id=topic_id, topic=topic, class_num=class_num)


@russian_bp.route("/russian/vocabulary-menu")
def russian_vocabulary_menu():
    class_num = get_int_arg("class", default=1, min_value=1, max_value=3)
    return render_template("russian/vocabulary_menu.html", student=get_student(), class_num=class_num)


@russian_bp.route("/russian/vocabulary")
def russian_vocabulary_list():
    class_num = get_int_arg("class", default=1, min_value=1, max_value=3)
    try:
        words = get_russian_vocabulary_items_for_class(class_num)
        error_message = None
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        words = []
        error_message = f"Не удалось получить словарные слова из БД: {error}"
    return render_template("russian/vocabulary_list.html", student=get_student(), class_num=class_num, words=words, error_message=error_message)


@russian_bp.route("/russian/rules")
def russian_rules():
    return russian_learning()


@russian_bp.route("/russian/test_setup")
def russian_test_setup():
    class_num = get_int_arg("class", default=1, min_value=1, max_value=11)
    return render_template("russian/test_setup.html", class_1_topics=build_topic_options(get_russian_topics(class_num if class_num in {1, 2, 3} else 1)), student=get_student())


@russian_bp.route("/russian/test")
def russian_test():
    student = get_student()
    class_num = request.args.get("class", "all")
    topic_id = request.args.get("type", "")
    total_requested = get_int_arg("words", default=25, min_value=1, max_value=50)
    if topic_id == CONTROL_SLICE_TYPE:
        total_requested = 50
    if class_num in {"1", "2", "3"} and topic_id:
        return render_template("russian/topic_test_radio.html", test_settings={"classNum": class_num, "topicId": topic_id}, total_questions=total_requested, student=student)
    if class_num not in {"1", "2", "3", "all"}:
        class_num = "all"
    try:
        all_available = get_russian_vocabulary_words_for_test(class_num)
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return render_template("russian/test.html", test_words=[], total_words=0, student=student, error_message=f"Не удалось получить словарные слова из БД: {error}")
    random.shuffle(all_available)
    if not all_available:
        test_words = []
    elif len(all_available) >= total_requested:
        test_words = all_available[:total_requested]
    else:
        test_words = all_available + random.choices(all_available, k=total_requested - len(all_available))
    return render_template("russian/test.html", test_words=test_words, total_words=total_requested, student=student)


@russian_bp.route("/russian/generate_task", methods=["POST"])
def generate_russian_task():
    data, error_response = get_json_body()
    if error_response:
        return error_response
    class_num = normalize_class_num(data.get("class"), default=1)
    topic_id = str(data.get("topic", DEFAULT_TOPIC_BY_CLASS.get(class_num, "sounds_and_letters"))).strip()
    if topic_id == CONTROL_SLICE_TYPE:
        topic_id = get_next_control_topic_id(class_num)
    used_questions = normalize_used_questions(data.get("used_questions"))
    if class_num == 3:
        task = generate_russian_class_3_topic_task(topic_id, used_questions=used_questions)
    elif class_num == 2:
        task = generate_russian_class_2_topic_task(topic_id, used_questions=used_questions)
    else:
        task = generate_russian_class_1_topic_task(topic_id, used_questions=used_questions)
    return jsonify(ensure_unique_task(task, used_questions))


@russian_bp.route("/russian/check_task", methods=["POST"])
def check_russian_task():
    data, error_response = get_json_body()
    if error_response:
        return error_response
    user_answer = data.get("answer", "")
    correct_answer = data.get("correct")
    if correct_answer is None:
        return jsonify({"result": "error", "message": "Не передан правильный ответ"}), 400
    if str(user_answer).strip() == "":
        return jsonify({"result": "empty", "correct_answer": correct_answer})
    is_correct = normalize_text(user_answer) == normalize_text(correct_answer)
    return jsonify({"result": "correct" if is_correct else "incorrect", "correct_answer": correct_answer})
