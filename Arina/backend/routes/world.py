from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request

from Arina.backend.routes.common import get_int_arg, get_json_body, get_student
from Arina.world.class_1_tasks import generate_world_class_1_topic_task, get_topic_options_for_select, normalize_text
from Arina.world.class_1_topics import WORLD_CLASS_1_TOPICS, get_world_class_1_topic

world_bp = Blueprint("world", __name__)

SUPPORTED_WORLD_CLASSES = list(range(1, 12))
IMPLEMENTED_TEST_CLASSES = {1}
IMPLEMENTED_LEARNING_CLASSES = {1}


def normalize_used_questions(raw_used_questions: Any) -> list[str]:
    if not isinstance(raw_used_questions, list):
        return []

    normalized = []
    for question in raw_used_questions:
        question_text = str(question).strip()
        if question_text:
            normalized.append(question_text)

    return normalized[-300:]


@world_bp.route("/world")
def world_menu():
    return render_template(
        "world/menu.html",
        student=get_student(),
        classes=SUPPORTED_WORLD_CLASSES,
        implemented_test_classes=IMPLEMENTED_TEST_CLASSES,
        implemented_learning_classes=IMPLEMENTED_LEARNING_CLASSES,
    )


@world_bp.route("/world/class/<int:class_num>")
def world_class_page(class_num: int):
    if class_num not in SUPPORTED_WORLD_CLASSES:
        abort(404)

    if class_num == 1:
        return render_template(
            "world/learning.html",
            student=get_student(),
            class_1_topics=WORLD_CLASS_1_TOPICS,
        )

    return render_template(
        "world/class_page.html",
        student=get_student(),
        class_num=class_num,
        is_learning_implemented=False,
        is_testing_implemented=False,
    )


@world_bp.route("/world/learning")
def world_learning():
    class_num = get_int_arg("class", default=1, min_value=1, max_value=11)

    if class_num != 1:
        return render_template(
            "world/class_page.html",
            student=get_student(),
            class_num=class_num,
            is_learning_implemented=False,
            is_testing_implemented=False,
        )

    return render_template(
        "world/learning.html",
        student=get_student(),
        class_1_topics=WORLD_CLASS_1_TOPICS,
    )


@world_bp.route("/world/learning/topic/<topic_id>")
def world_learning_topic(topic_id: str):
    topic = get_world_class_1_topic(topic_id)

    if not topic:
        abort(404)

    return render_template(
        "world/learning_topic.html",
        student=get_student(),
        topic_id=topic_id,
        topic=topic,
    )


@world_bp.route("/world/test_setup")
def world_test_setup():
    return render_template(
        "world/test_setup.html",
        student=get_student(),
        class_1_topics=get_topic_options_for_select(),
    )


@world_bp.route("/world/test")
def world_test():
    topic_id = request.args.get("type", "living_nonliving")
    total_requested = get_int_arg("questions", default=25, min_value=1, max_value=200)

    return render_template(
        "world/topic_test.html",
        test_settings={"classNum": "1", "topicId": topic_id or "living_nonliving"},
        total_questions=total_requested,
        student=get_student(),
    )


@world_bp.route("/world/generate_task", methods=["POST"])
def generate_world_task():
    data, error_response = get_json_body()

    if error_response:
        return error_response

    topic_id = str(data.get("topic", "living_nonliving")).strip() or "living_nonliving"
    used_questions = normalize_used_questions(data.get("used_questions"))
    task = generate_world_class_1_topic_task(topic_id, used_questions=used_questions)
    return jsonify(task)


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
