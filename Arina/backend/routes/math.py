import random
from typing import Any, Optional

from flask import Blueprint, abort, jsonify, render_template, request

from Arina.backend.routes.common import get_int_arg, get_json_body, get_student
from Arina.backend.services.catalog import build_topic_options, get_topic_or_none, merge_db_topics_with_content
from Arina.math.class_1 import MathExamplesClass1
from Arina.math.class_1_topics import CLASS_1_MATH_TOPICS
from Arina.math.class_2 import MathExamplesClass2
from Arina.math.class_3 import MathExamplesClass3
from Arina.utils.safe_math import SafeMathExpressionError, safe_eval_math_expr

math_bp = Blueprint("math", __name__)

SUPPORTED_MATH_CLASSES = list(range(1, 12))
IMPLEMENTED_TEST_CLASSES = {1, 2, 3}
IMPLEMENTED_LEARNING_CLASSES = {1}
CONTROL_SLICE_TYPE = "control_slice"
control_topic_cursor = 0


def get_math_class_1_topics() -> dict:
    return merge_db_topics_with_content("math", 1, CLASS_1_MATH_TOPICS)


def get_math_class_1_topic(topic_id: str) -> dict | None:
    return get_topic_or_none("math", 1, topic_id, CLASS_1_MATH_TOPICS)


def get_control_topic_id(question_number: Any, topics: dict) -> str:
    global control_topic_cursor
    topic_ids = list(topics.keys())
    if not topic_ids:
        return "add_sub_to_20"
    try:
        index = int(question_number) - 1
    except (TypeError, ValueError):
        index = control_topic_cursor
        control_topic_cursor += 1
    return topic_ids[index % len(topic_ids)]


def normalize_class_num(raw_class: Any, default: int = 1) -> int:
    try:
        class_num = int(raw_class)
    except (TypeError, ValueError):
        return default
    return class_num if class_num in (1, 2, 3) else default


def normalize_math_type(class_num: int, example_type: str) -> str:
    if not example_type:
        return "all"
    example_type = str(example_type).strip()
    allowed_for_class_1 = set(get_math_class_1_topics().keys()) | {CONTROL_SLICE_TYPE, "all", "addsub", "+", "-"}
    allowed_for_class_2 = {"all", "addsub", "+", "-"}
    allowed_for_class_3 = {"all", "addsub", "muldiv", "+", "-", "*", "/", "simple_equation", "parentheses"}
    if class_num == 1:
        return example_type if example_type in allowed_for_class_1 else "add_sub_to_20"
    if class_num == 2:
        return example_type if example_type in allowed_for_class_2 else "all"
    return example_type if example_type in allowed_for_class_3 else "all"


def normalize_used_questions(raw_used_questions: Any) -> list[str]:
    if not isinstance(raw_used_questions, list):
        return []
    return [str(question).strip() for question in raw_used_questions if str(question).strip()][-300:]


def build_allowed_ops(example_type: str) -> list[str]:
    return {"addsub": ["+", "-"], "muldiv": ["*", "/"], "all": ["+", "-", "*", "/"], "+": ["+"], "-": ["-"], "*": ["*"], "/": ["/"]}.get(example_type, ["+", "-", "*", "/"])


def parse_user_answer(raw_answer: Any) -> Optional[int]:
    try:
        return int(str(raw_answer).strip())
    except (TypeError, ValueError):
        return None


def normalize_text_answer(value: Any) -> str:
    return str(value).strip().lower().replace("ё", "е")


def calculate_basic_answer(class_num: int, example_type: str, table_num: str, a: Any, op: str, b: Any) -> Optional[int]:
    try:
        a_int = int(a)
        b_int = int(b)
    except (TypeError, ValueError):
        return None
    if class_num == 1:
        math = MathExamplesClass1(example_type, table_num)
    elif class_num == 2:
        math = MathExamplesClass2(example_type, table_num)
    else:
        math = MathExamplesClass3(example_type, table_num)
    return math.calculate_answer(a_int, op, b_int)


@math_bp.route("/math")
def math_menu():
    return render_template("math/menu.html", student=get_student(), classes=SUPPORTED_MATH_CLASSES, implemented_test_classes=IMPLEMENTED_TEST_CLASSES, implemented_learning_classes=IMPLEMENTED_LEARNING_CLASSES)


@math_bp.route("/math/class/<int:class_num>")
def math_class_page(class_num: int):
    if class_num not in SUPPORTED_MATH_CLASSES:
        abort(404)
    if class_num == 1:
        return render_template("math/learning.html", student=get_student(), class_1_topics=get_math_class_1_topics(), from_class_page=True)
    return render_template("math/class_page.html", student=get_student(), class_num=class_num, is_learning_implemented=class_num in IMPLEMENTED_LEARNING_CLASSES, is_testing_implemented=class_num in IMPLEMENTED_TEST_CLASSES)


@math_bp.route("/math/learning")
def math_learning():
    class_num = get_int_arg("class", default=1, min_value=1, max_value=11)
    if class_num != 1:
        return render_template("math/class_page.html", student=get_student(), class_num=class_num, is_learning_implemented=False, is_testing_implemented=class_num in IMPLEMENTED_TEST_CLASSES)
    return render_template("math/learning.html", student=get_student(), class_1_topics=get_math_class_1_topics(), from_class_page=False)


@math_bp.route("/math/learning/topic/<topic_id>")
def math_learning_topic(topic_id: str):
    topic = get_math_class_1_topic(topic_id)
    if not topic:
        abort(404)
    return render_template("math/learning_topic.html", student=get_student(), topic_id=topic_id, topic=topic)


@math_bp.route("/math/test_setup")
def math_test_setup():
    return render_template("math/test_setup.html", student=get_student(), class_1_topics=build_topic_options(get_math_class_1_topics()))


@math_bp.route("/math/test")
def math_test():
    student = get_student()
    total_questions = get_int_arg("questions", default=25, min_value=1, max_value=50)
    if request.args.get("type") == CONTROL_SLICE_TYPE:
        total_questions = 50
    test_settings = {"classNum": request.args.get("class", "1"), "exampleType": request.args.get("type", "add_sub_to_20"), "tableNum": request.args.get("table", "all"), "includeEquations": request.args.get("equations") == "true", "includeParentheses": request.args.get("parentheses") == "true", "isSpeedMode": request.args.get("speed") == "true"}
    return render_template("math/test.html", test_settings=test_settings, total_questions=total_questions, student=student)


@math_bp.route("/generate_example", methods=["POST"])
def generate_example():
    data, error_response = get_json_body()
    if error_response:
        return error_response
    class_num = normalize_class_num(data.get("class"), default=1)
    example_type = normalize_math_type(class_num, data.get("type", "add_sub_to_20" if class_num == 1 else "all"))
    table_num = data.get("table_num", "all")
    include_equation = bool(data.get("include_equation"))
    include_parentheses = bool(data.get("include_parentheses"))
    used_questions = normalize_used_questions(data.get("used_questions"))
    allowed_ops = build_allowed_ops(example_type)
    if class_num == 1:
        if example_type == CONTROL_SLICE_TYPE:
            example_type = get_control_topic_id(data.get("question_number"), get_math_class_1_topics())
        math = MathExamplesClass1(example_type, table_num, used_questions=used_questions)
        example = math.generate_example()
        if "question" in example and "correct" in example:
            return jsonify(example)
        correct = math.calculate_answer(example["a"], example["op"], example["b"])
        example["correct"] = correct
        example["answer_type"] = "number"
        return jsonify(example)
    if class_num == 2:
        math = MathExamplesClass2(example_type, table_num)
        example = math.generate_example()
        correct = math.calculate_answer(example["a"], example["op"], example["b"])
        example["correct"] = correct
        return jsonify(example)
    math = MathExamplesClass3(example_type, table_num)
    options = ["default"]
    if include_equation and any(op in allowed_ops for op in ["+", "-"]):
        options.append("equation")
    if include_parentheses:
        options.append("parentheses")
    selected = random.choice(options)
    if selected == "equation":
        example = math.generate_simple_equation(allowed_ops=allowed_ops)
        example["correct"] = example["x"]
        return jsonify(example)
    if selected == "parentheses":
        example = math.generate_parentheses_example(allowed_ops=allowed_ops)
        expr = example.get("expr", "")
        try:
            correct = safe_eval_math_expr(expr)
        except SafeMathExpressionError:
            correct = None
        example["correct"] = correct
        return jsonify(example)
    example = math.generate_example()
    correct = math.calculate_answer(example["a"], example["op"], example["b"])
    example["correct"] = correct
    return jsonify(example)


@math_bp.route("/check_answer", methods=["POST"])
def check_answer():
    data, error_response = get_json_body()
    if error_response:
        return error_response
    if "answer" not in data:
        return jsonify({"result": "error", "message": "Не передан ответ"}), 400
    class_num = normalize_class_num(data.get("class"), default=1)
    example_type = normalize_math_type(class_num, data.get("type", "add_sub_to_20" if class_num == 1 else "all"))
    table_num = data.get("table_num", "all")
    user_answer = data.get("answer")
    answer_type = data.get("answer_type")
    direct_correct = data.get("correct")
    if direct_correct is not None:
        if answer_type == "choice" or isinstance(direct_correct, str):
            status = "correct" if normalize_text_answer(user_answer) == normalize_text_answer(direct_correct) else "incorrect"
            return jsonify({"result": status, "correct_answer": direct_correct})
        user_answer_num = parse_user_answer(user_answer)
        correct_num = parse_user_answer(direct_correct)
        if user_answer_num is None or correct_num is None:
            return jsonify({"result": "error", "message": "Введите число"}), 400
        status = "correct" if user_answer_num == correct_num else "incorrect"
        return jsonify({"result": status, "correct_answer": correct_num})
    user_answer_num = parse_user_answer(user_answer)
    if user_answer_num is None:
        return jsonify({"result": "error", "message": "Введите число"}), 400
    a = data.get("a")
    b = data.get("b")
    op = data.get("op")
    correct = calculate_basic_answer(class_num, example_type, table_num, a, op, b)
    if correct is None:
        return jsonify({"result": "error", "message": "Некорректный пример"}), 400
    status = "correct" if user_answer_num == correct else "incorrect"
    return jsonify({"result": status, "correct_answer": correct})
