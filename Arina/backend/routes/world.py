from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request

from Arina.backend.routes.common import get_int_arg, get_json_body, get_student
from Arina.backend.services.catalog import build_topic_options, get_topic_or_none, merge_db_topics_with_content
from Arina.world.class_1_tasks import generate_world_class_1_topic_task, normalize_text
from Arina.world.class_1_topics import WORLD_CLASS_1_TOPICS
from Arina.world.class_2_tasks import generate_world_class_2_topic_task
from Arina.world.class_2_topics import WORLD_CLASS_2_TOPICS
from Arina.world.class_3_tasks import generate_world_class_3_topic_task
from Arina.world.class_3_topics import WORLD_CLASS_3_TOPICS

world_bp = Blueprint("world", __name__)

SUPPORTED_WORLD_CLASSES = list(range(1, 12))
IMPLEMENTED_TEST_CLASSES = {1, 2, 3}
IMPLEMENTED_LEARNING_CLASSES = {1, 2, 3}
CONTROL_SLICE_TYPE = "control_slice"
control_topic_cursor = 0
TOPICS_BY_CLASS = {1: WORLD_CLASS_1_TOPICS, 2: WORLD_CLASS_2_TOPICS, 3: WORLD_CLASS_3_TOPICS}
DEFAULT_TOPIC_BY_CLASS = {1: "living_nonliving", 2: "nature_living_nonliving_2", 3: "earth_planet"}


def get_world_topics(class_num: int) -> dict:
    return merge_db_topics_with_content("world", class_num, TOPICS_BY_CLASS.get(class_num, WORLD_CLASS_1_TOPICS))


def get_world_topic_from_catalog(class_num: int, topic_id: str) -> dict | None:
    return get_topic_or_none("world", class_num, topic_id, TOPICS_BY_CLASS.get(class_num, WORLD_CLASS_1_TOPICS))


def get_next_control_topic_id(class_num: int) -> str:
    global control_topic_cursor
    topic_ids = list(get_world_topics(class_num).keys())
    if not topic_ids:
        return DEFAULT_TOPIC_BY_CLASS.get(class_num, "living_nonliving")
    topic_id = topic_ids[control_topic_cursor % len(topic_ids)]
    control_topic_cursor += 1
    return topic_id


def normalize_used_questions(raw_used_questions: Any) -> list[str]:
    if not isinstance(raw_used_questions, list):
        return []
    return [str(question).strip() for question in raw_used_questions if str(question).strip()][-300:]


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


def normalize_class_num(raw_class: Any, default: int = 1) -> int:
    try:
        class_num = int(raw_class)
    except (TypeError, ValueError):
        return default
    return class_num if class_num in {1, 2, 3} else default


@world_bp.route("/world")
def world_menu():
    return render_template("world/menu.html", student=get_student(), classes=SUPPORTED_WORLD_CLASSES, implemented_test_classes=IMPLEMENTED_TEST_CLASSES, implemented_learning_classes=IMPLEMENTED_LEARNING_CLASSES)


@world_bp.route("/world/class/<int:class_num>")
def world_class_page(class_num: int):
    if class_num not in SUPPORTED_WORLD_CLASSES:
        abort(404)
    if class_num in IMPLEMENTED_LEARNING_CLASSES:
        return render_template("world/learning.html", student=get_student(), topics=get_world_topics(class_num), class_num=class_num)
    return render_template("world/class_page.html", student=get_student(), class_num=class_num, is_learning_implemented=False, is_testing_implemented=False)


@world_bp.route("/world/learning")
def world_learning():
    class_num = get_int_arg("class", default=1, min_value=1, max_value=11)
    if class_num not in IMPLEMENTED_LEARNING_CLASSES:
        return render_template("world/class_page.html", student=get_student(), class_num=class_num, is_learning_implemented=False, is_testing_implemented=False)
    return render_template("world/learning.html", student=get_student(), topics=get_world_topics(class_num), class_num=class_num)


@world_bp.route("/world/learning/topic/<topic_id>")
def world_learning_topic(topic_id: str):
    class_num = get_int_arg("class", default=1, min_value=1, max_value=11)
    topic = get_world_topic_from_catalog(class_num, topic_id)
    if not topic:
        abort(404)
    return render_template("world/learning_topic.html", student=get_student(), topic_id=topic_id, topic=topic, class_num=class_num)


@world_bp.route("/world/test_setup")
def world_test_setup():
    class_num = get_int_arg("class", default=1, min_value=1, max_value=11)
    return render_template("world/test_setup.html", student=get_student(), class_1_topics=build_topic_options(get_world_topics(class_num if class_num in {1, 2, 3} else 1)))


@world_bp.route("/world/test")
def world_test():
    class_num = get_int_arg("class", default=1, min_value=1, max_value=11)
    topic_id = request.args.get("type", DEFAULT_TOPIC_BY_CLASS.get(class_num, "living_nonliving"))
    total_requested = get_int_arg("questions", default=25, min_value=1, max_value=50)
    if topic_id == CONTROL_SLICE_TYPE:
        total_requested = 50
    return render_template("world/topic_test.html", test_settings={"classNum": str(class_num), "topicId": topic_id}, total_questions=total_requested, student=get_student())


@world_bp.route("/world/generate_task", methods=["POST"])
def generate_world_task():
    data, error_response = get_json_body()
    if error_response:
        return error_response
    class_num = normalize_class_num(data.get("class"), default=1)
    topic_id = str(data.get("topic", DEFAULT_TOPIC_BY_CLASS.get(class_num, "living_nonliving"))).strip()
    if topic_id == CONTROL_SLICE_TYPE:
        topic_id = get_next_control_topic_id(class_num)
    used_questions = normalize_used_questions(data.get("used_questions"))
    if class_num == 3:
        task = generate_world_class_3_topic_task(topic_id, used_questions=used_questions)
    elif class_num == 2:
        task = generate_world_class_2_topic_task(topic_id, used_questions=used_questions)
    else:
        task = generate_world_class_1_topic_task(topic_id, used_questions=used_questions)
    return jsonify(ensure_unique_task(task, used_questions))


@world_bp.route("/world/check_task", methods=["POST"])
def check_world_task():
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
