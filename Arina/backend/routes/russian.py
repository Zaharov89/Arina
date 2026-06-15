import random
from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from Arina.backend.routes.common import get_int_arg, get_json_body, get_student
from Arina.backend.services.catalog import build_topic_options, get_topic_or_none, merge_db_topics_with_content
from Arina.database.session import get_session_factory
from Arina.russian_language.class_1_tasks import generate_russian_class_1_topic_task, normalize_text
from Arina.russian_language.class_1_topics import RUSSIAN_CLASS_1_TOPICS
from Arina.russian_language.vocabulary import get_russian_vocabulary_word_list

russian_bp = Blueprint("russian", __name__)

SUPPORTED_RUSSIAN_CLASSES = list(range(1, 12))
IMPLEMENTED_TEST_CLASSES = {1, 2, 3}
IMPLEMENTED_LEARNING_CLASSES = {1}
CONTROL_SLICE_TYPE = "control_slice"
control_topic_cursor = 0


def get_russian_class_1_topics() -> dict:
    return merge_db_topics_with_content("russian", 1, RUSSIAN_CLASS_1_TOPICS)


def get_russian_class_1_topic_from_catalog(topic_id: str) -> dict | None:
    return get_topic_or_none("russian", 1, topic_id, RUSSIAN_CLASS_1_TOPICS)


def get_next_control_topic_id() -> str:
    global control_topic_cursor
    topic_ids = list(get_russian_class_1_topics().keys())
    if not topic_ids:
        return "sounds_and_letters"
    topic_id = topic_ids[control_topic_cursor % len(topic_ids)]
    control_topic_cursor += 1
    return topic_id


def get_russian_vocabulary_words_for_class(class_num: str) -> list[str]:
    class_number = None if class_num == "all" else int(class_num)
    session_factory = get_session_factory()
    with session_factory() as session:
        return get_russian_vocabulary_word_list(session, class_number)


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
    student = get_student()
    return render_template("russian/menu.html", classes=SUPPORTED_RUSSIAN_CLASSES, implemented_test_classes=IMPLEMENTED_TEST_CLASSES, implemented_learning_classes=IMPLEMENTED_LEARNING_CLASSES, student=student)


@russian_bp.route("/russian/class/<int:class_num>")
def russian_class_page(class_num: int):
    if class_num not in SUPPORTED_RUSSIAN_CLASSES:
        abort(404)
    if class_num == 1:
        return render_template("russian/learning.html", student=get_student(), class_1_topics=get_russian_class_1_topics(), from_class_page=True)
    return render_template("russian/class_page.html", student=get_student(), class_num=class_num, is_learning_implemented=class_num in IMPLEMENTED_LEARNING_CLASSES, is_testing_implemented=class_num in IMPLEMENTED_TEST_CLASSES)


@russian_bp.route("/russian/learning")
def russian_learning():
    class_num = get_int_arg("class", default=1, min_value=1, max_value=11)
    if class_num != 1:
        return render_template("russian/class_page.html", student=get_student(), class_num=class_num, is_learning_implemented=False, is_testing_implemented=class_num in IMPLEMENTED_TEST_CLASSES)
    return render_template("russian/learning.html", student=get_student(), class_1_topics=get_russian_class_1_topics(), from_class_page=False)


@russian_bp.route("/russian/learning/topic/<topic_id>")
def russian_learning_topic(topic_id: str):
    topic = get_russian_class_1_topic_from_catalog(topic_id)
    if not topic:
        abort(404)
    return render_template("russian/learning_topic.html", student=get_student(), topic_id=topic_id, topic=topic)


@russian_bp.route("/russian/rules")
def russian_rules():
    return russian_learning()


@russian_bp.route("/russian/test_setup")
def russian_test_setup():
    student = get_student()
    return render_template("russian/test_setup.html", class_1_topics=build_topic_options(get_russian_class_1_topics()), student=student)


@russian_bp.route("/russian/test")
def russian_test():
    student = get_student()
    class_num = request.args.get("class", "all")
    topic_id = request.args.get("type", "")
    total_requested = get_int_arg("words", default=25, min_value=1, max_value=50)
    if topic_id == CONTROL_SLICE_TYPE:
        total_requested = 50
    if class_num == "1" and topic_id:
        return render_template("russian/topic_test_radio.html", test_settings={"classNum": "1", "topicId": topic_id}, total_questions=total_requested, student=student)
    if class_num not in {"1", "2", "3", "all"}:
        class_num = "all"
    try:
        all_available = get_russian_vocabulary_words_for_class(class_num)
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return render_template("russian/test.html", test_words=[], total_words=0, student=student, error_message=f"Не удалось получить словарные слова из БД: {error}")
    if not all_available:
        test_words = []
    elif len(all_available) >= total_requested:
        test_words = random.sample(all_available, total_requested)
    else:
        test_words = random.choices(all_available, k=total_requested)
    return render_template("russian/test.html", test_words=test_words, total_words=total_requested, student=student)


@russian_bp.route("/russian/generate_task", methods=["POST"])
def generate_russian_task():
    data, error_response = get_json_body()
    if error_response:
        return error_response
    class_num = normalize_class_num(data.get("class"), default=1)
    if class_num != 1:
        return jsonify({"error": "Topic tasks are available only for Russian class 1"}), 400
    topic_id = str(data.get("topic", "sounds_and_letters")).strip() or "sounds_and_letters"
    if topic_id == CONTROL_SLICE_TYPE:
        topic_id = get_next_control_topic_id()
    used_questions = normalize_used_questions(data.get("used_questions"))
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
