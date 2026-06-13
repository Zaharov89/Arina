import random
from typing import Any, Optional

from flask import Blueprint, jsonify, render_template, request

from Arina.backend.routes.common import get_int_arg, get_json_body, get_student
from Arina.math.class_1 import MathExamplesClass1
from Arina.math.class_2 import MathExamplesClass2
from Arina.math.class_3 import MathExamplesClass3
from Arina.utils.safe_math import SafeMathExpressionError, safe_eval_math_expr

math_bp = Blueprint("math", __name__)


def normalize_class_num(raw_class: Any, default: int = 1) -> int:
    try:
        class_num = int(raw_class)
    except (TypeError, ValueError):
        return default

    if class_num not in (1, 2, 3):
        return default

    return class_num


def normalize_math_type(class_num: int, example_type: str) -> str:
    if not example_type:
        return "all"

    example_type = str(example_type).strip()

    allowed_for_class_1_2 = {"all", "addsub", "+", "-"}
    allowed_for_class_3 = {
        "all",
        "addsub",
        "muldiv",
        "+",
        "-",
        "*",
        "/",
        "simple_equation",
        "parentheses",
    }

    if class_num in (1, 2):
        return example_type if example_type in allowed_for_class_1_2 else "all"

    return example_type if example_type in allowed_for_class_3 else "all"


def build_allowed_ops(example_type: str) -> list[str]:
    return {
        "addsub": ["+", "-"],
        "muldiv": ["*", "/"],
        "all": ["+", "-", "*", "/"],
        "+": ["+"],
        "-": ["-"],
        "*": ["*"],
        "/": ["/"],
    }.get(example_type, ["+", "-", "*", "/"])


def parse_user_answer(raw_answer: Any) -> Optional[int]:
    try:
        return int(str(raw_answer).strip())
    except (TypeError, ValueError):
        return None


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
    return render_template("math/menu.html", student=get_student())


@math_bp.route("/math/test_setup")
def math_test_setup():
    return render_template("math/test_setup.html", student=get_student())


@math_bp.route("/math/test")
def math_test():
    student = get_student()
    total_questions = get_int_arg("questions", default=25, min_value=1, max_value=200)

    test_settings = {
        "classNum": request.args.get("class", "1"),
        "exampleType": request.args.get("type", "all"),
        "tableNum": request.args.get("table", "all"),
        "includeEquations": request.args.get("equations") == "true",
        "includeParentheses": request.args.get("parentheses") == "true",
        "isSpeedMode": request.args.get("speed") == "true",
    }

    return render_template(
        "math/test.html",
        test_settings=test_settings,
        total_questions=total_questions,
        student=student,
    )


@math_bp.route("/generate_example", methods=["POST"])
def generate_example():
    data, error_response = get_json_body()

    if error_response:
        return error_response

    class_num = normalize_class_num(data.get("class"), default=1)
    example_type = normalize_math_type(class_num, data.get("type", "all"))
    table_num = data.get("table_num", "all")
    include_equation = bool(data.get("include_equation"))
    include_parentheses = bool(data.get("include_parentheses"))

    allowed_ops = build_allowed_ops(example_type)

    if class_num == 1:
        math = MathExamplesClass1(example_type, table_num)
        example = math.generate_example()
        correct = math.calculate_answer(example["a"], example["op"], example["b"])
        example["correct"] = correct
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
    example_type = normalize_math_type(class_num, data.get("type", "all"))
    table_num = data.get("table_num", "all")
    user_answer = data.get("answer")

    user_answer_num = parse_user_answer(user_answer)

    if user_answer_num is None:
        return jsonify({"result": "error", "message": "Введите число"}), 400

    a = data.get("a")
    op = data.get("op")
    b = data.get("b")
    expr = data.get("expr", "")
    x_val = data.get("x")

    if x_val is not None and str(x_val).strip() != "":
        try:
            correct = int(x_val)
        except (TypeError, ValueError):
            return jsonify({"result": "error", "message": "Некорректное значение x"}), 400

        status = "correct" if user_answer_num == correct else "incorrect"
        return jsonify({"result": status, "correct_answer": correct})

    if expr:
        try:
            correct = safe_eval_math_expr(str(expr).replace(" ", ""))
        except SafeMathExpressionError:
            return jsonify({"result": "error", "message": "Ошибка формата примера"}), 400

        status = "correct" if user_answer_num == correct else "incorrect"
        return jsonify({"result": status, "correct_answer": correct})

    if a is not None and op is not None and b is not None:
        correct = calculate_basic_answer(class_num, example_type, table_num, a, op, b)

        if correct is None:
            return jsonify({"result": "error", "message": "Ошибка формата примера"}), 400

        status = "correct" if user_answer_num == correct else "incorrect"
        return jsonify({"result": status, "correct_answer": correct})

    return jsonify({"result": "error", "message": "Ошибка формата примера"}), 400
