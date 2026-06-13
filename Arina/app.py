import random
import subprocess
import sys
import threading
import time
from typing import Any, Dict, Optional, Tuple

from flask import Flask, jsonify, render_template, request

# === ЯВНЫЕ ИМПОРТЫ ДЛЯ PYINSTALLER (НЕ УДАЛЯТЬ!) ===
import Arina.russian_language.class_2
import Arina.russian_language.class_3
import Arina.english_language.class_2
import Arina.english_language.class_3
import Arina.math.class_1
import Arina.math.class_2
import Arina.math.class_3
import Arina.utils.safe_math
# ===================================================

from Arina.config import DEFAULT_STUDENT, FLASK_HOST, FLASK_PORT
from Arina.english_language.class_2 import class2Words
from Arina.english_language.class_3 import class3Words
from Arina.math.class_1 import MathExamplesClass1
from Arina.math.class_2 import MathExamplesClass2
from Arina.math.class_3 import MathExamplesClass3
from Arina.russian_language.class_2 import russianQuestions as questions2
from Arina.russian_language.class_3 import russianQuestions as questions3
from Arina.utils.safe_math import SafeMathExpressionError, safe_eval_math_expr


app = Flask(__name__)


# === ПОДКЛЮЧЕНИЕ СТАТИСТИКИ ===
try:
    from Arina.stats.routes import stats_bp
except ImportError:
    from stats.routes import stats_bp

app.register_blueprint(stats_bp)
print(f"✅ Blueprint 'stats' зарегистрирован: {app.blueprints.get('stats')}")


# === ОБЩИЕ HELPERS ===
def get_student() -> str:
    student = request.args.get("student", DEFAULT_STUDENT)
    return student.strip() or DEFAULT_STUDENT


def get_int_arg(name: str, default: int, min_value: int, max_value: int) -> int:
    raw_value = request.args.get(name, default)

    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return default

    return max(min_value, min(value, max_value))


def get_json_body() -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[Any, int]]]:
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None, (jsonify({"error": "JSON body is required"}), 400)

    return data, None


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


# === МАРШРУТЫ ===
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/subjects")
def subjects_menu():
    return render_template("subjects.html", student=get_student())


@app.route("/student_selection")
def student_selection():
    return render_template("student_selection/index.html")


# === АНГЛИЙСКИЙ ЯЗЫК ===
@app.route("/english/menu")
def english_menu():
    student = get_student()
    return render_template(
        "english/menu.html",
        class2_words=class2Words,
        class3_words=class3Words,
        student=student,
    )


@app.route("/english/vocabulary")
def english_vocabulary():
    student = get_student()
    return render_template(
        "english/vocabulary.html",
        class2_words=class2Words,
        class3_words=class3Words,
        student=student,
    )


@app.route("/english/rules")
def english_rules():
    student = get_student()
    return render_template(
        "english/rules.html",
        class2_words=class2Words,
        class3_words=class3Words,
        student=student,
    )


@app.route("/english/test_setup")
def english_test_setup():
    student = get_student()
    return render_template(
        "english/test_setup.html",
        class2_words=class2Words,
        class3_words=class3Words,
        student=student,
    )


@app.route("/english/test")
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


# === РУССКИЙ ЯЗЫК ===
@app.route("/russian")
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


@app.route("/russian/rules")
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


@app.route("/russian/test_setup")
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


@app.route("/russian/test")
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


# === МАТЕМАТИКА ===
@app.route("/math")
def math_menu():
    return render_template("math/menu.html", student=get_student())


@app.route("/math/test_setup")
def math_test_setup():
    return render_template("math/test_setup.html", student=get_student())


@app.route("/math/test")
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


# === API ===
@app.route("/generate_example", methods=["POST"])
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


@app.route("/check_answer", methods=["POST"])
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


@app.route("/questions")
def questions():
    mode = request.args.get("mode", "all")

    if mode == "2":
        return jsonify(questions2)

    if mode == "3":
        return jsonify(questions3)

    if mode == "en_all":
        return jsonify(class2Words + class3Words)

    if mode == "en_2":
        return jsonify(class2Words)

    if mode == "en_3":
        return jsonify(class3Words)

    if mode == "all":
        all_questions = {**questions2, **questions3}
        return jsonify(all_questions)

    return jsonify({})


# === РЕЗУЛЬТАТЫ ===
@app.route("/results/english")
def results_english():
    return render_template("results/english/results.html", student=get_student())


@app.route("/results/russian")
def results_russian():
    return render_template("results/russian/results.html", student=get_student())


@app.route("/results/math")
def results_math():
    return render_template("results/math/results.html", student=get_student())


# === ЗАПУСК СЕРВЕРА ===
def run_flask():
    app.run(debug=False, host=FLASK_HOST, port=FLASK_PORT)


def open_browser():
    time.sleep(2)
    url = f"http://{FLASK_HOST}:{FLASK_PORT}"

    if sys.platform == "win32":
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        try:
            subprocess.Popen([chrome_path, "--new-window", url])
        except FileNotFoundError:
            subprocess.Popen(["cmd", "/c", "start", "", url], shell=True)

    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-n", "-a", "Google Chrome", url])

    else:
        subprocess.Popen(["xdg-open", url])


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    open_browser()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
