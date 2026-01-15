import os
import time
import threading
import sys
import subprocess
from flask import Flask, render_template, request, jsonify

# === ЯВНЫЕ ИМПОРТЫ ДЛЯ PYINSTALLER (НЕ УДАЛЯТЬ!) ===
import Arina.russian_language.class_2
import Arina.russian_language.class_3
import Arina.english_language.class_2
import Arina.english_language.class_3
import Arina.math.class_1
import Arina.math.class_2
import Arina.math.class_3
# ===================================================

# === ИМПОРТ ДАННЫХ ИЗ PYTHON-ФАЙЛОВ ===
from Arina.english_language.class_2 import class2Words
from Arina.english_language.class_3 import class3Words

# Импорты для других модулей
from Arina.math.class_1 import MathExamplesClass1
from Arina.math.class_2 import MathExamplesClass2
from Arina.math.class_3 import MathExamplesClass3
from Arina.russian_language.class_2 import russianQuestions as questions2
from Arina.russian_language.class_3 import russianQuestions as questions3

import random

app = Flask(__name__)

# === ПОДКЛЮЧЕНИЕ СТАТИСТИКИ ===
try:
    from stats.routes import stats_bp
    app.register_blueprint(stats_bp)
    print(f"✅ Blueprint 'stats' зарегистрирован: {app.blueprints.get('stats')}")
except Exception as e:
    print(f"❌ Не удалось подключить статистику: {e}")

# === МАРШРУТЫ ===
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/subjects')
def subjects_menu():
    student = request.args.get('student', 'Арина')
    return render_template('subjects.html', student=student)

@app.route('/student_selection')
def student_selection():
    return render_template('student_selection/index.html')

# === АНГЛИЙСКИЙ ЯЗЫК ===
@app.route('/english/menu')
def english_menu():
    student = request.args.get('student', 'Арина')
    return render_template('english/menu.html', class2_words=class2Words, class3_words=class3Words, student=student)

@app.route('/english/vocabulary')
def english_vocabulary():
    student = request.args.get('student', 'Арина')
    return render_template('english/vocabulary.html', class2_words=class2Words, class3_words=class3Words, student=student)

@app.route('/english/rules')
def english_rules():
    student = request.args.get('student', 'Арина')
    return render_template('english/rules.html', class2_words=class2Words, class3_words=class3Words, student=student)

@app.route('/english/test_setup')
def english_test_setup():
    student = request.args.get('student', 'Арина')
    return render_template('english/test_setup.html', class2_words=class2Words, class3_words=class3Words, student=student)

@app.route('/english/test')
def english_test():
    student = request.args.get('student', 'Арина')
    class_num = request.args.get('class', 'all')
    test_type = request.args.get('type', 'en_to_ru')
    total_requested = int(request.args.get('words', 25))

    if class_num == 'all':
        all_available = class2Words + class3Words
    elif class_num == '2':
        all_available = class2Words
    elif class_num == '3':
        all_available = class3Words
    else:
        all_available = class2Words + class3Words

    if len(all_available) >= total_requested:
        test_words = random.sample(all_available, total_requested)
    else:
        test_words = random.choices(all_available, k=total_requested)

    return render_template(
        'english/test.html',
        class2_words=class2Words,
        class3_words=class3Words,
        test_words=test_words,
        total_words=total_requested,
        test_type=test_type,
        student=student
    )

# === РУССКИЙ ЯЗЫК ===
@app.route('/russian')
def russian_menu():
    student = request.args.get('student', 'Арина')
    class2_words = list(questions2.keys())
    class3_words = list(questions3.keys())
    class1_words = []
    return render_template('russian/menu.html', class1_words=class1_words, class2_words=class2_words, class3_words=class3_words, student=student)

@app.route('/russian/rules')
def russian_rules():
    student = request.args.get('student', 'Арина')
    class2_words = list(questions2.keys())
    class3_words = list(questions3.keys())
    class1_words = []
    return render_template('russian/rules.html', class1_words=class1_words, class2_words=class2_words, class3_words=class3_words, student=student)

@app.route('/russian/test_setup')
def russian_test_setup():
    student = request.args.get('student', 'Арина')
    class2_words = list(questions2.keys())
    class3_words = list(questions3.keys())
    class1_words = []
    return render_template('russian/test_setup.html', class1_words=class1_words, class2_words=class2_words, class3_words=class3_words, student=student)

@app.route('/russian/test')
def russian_test():
    student = request.args.get('student', 'Арина')
    class_num = request.args.get('class', 'all')
    total_requested = int(request.args.get('words', 25))

    if class_num == '2':
        all_available = list(questions2.keys())
    elif class_num == '3':
        all_available = list(questions3.keys())
    else:
        all_available = list(set(list(questions2.keys()) + list(questions3.keys())))

    if len(all_available) >= total_requested:
        test_words = random.sample(all_available, total_requested)
    else:
        test_words = random.choices(all_available, k=total_requested)

    return render_template('russian/test.html',
                         test_words=test_words,
                         total_words=total_requested,
                         student=student)

# === МАТЕМАТИКА ===
@app.route('/math')
def math_menu():
    student = request.args.get('student', 'Арина')
    return render_template('math/menu.html', student=student)

@app.route('/math/test_setup')
def math_test_setup():
    student = request.args.get('student', 'Арина')
    return render_template('math/test_setup.html', student=student)

@app.route('/math/test')
def math_test():
    student = request.args.get('student', 'Аriна')
    test_settings = {
        'classNum': request.args.get('class', '1'),
        'exampleType': request.args.get('type', 'all'),
        'tableNum': request.args.get('table', 'all'),
        'includeEquations': request.args.get('equations') == 'true',
        'includeParentheses': request.args.get('parentheses') == 'true',
        'isSpeedMode': request.args.get('speed') == 'true'
    }
    total_questions = int(request.args.get('questions', 25))
    return render_template('math/test.html',
                         test_settings=test_settings,
                         total_questions=total_questions,
                         student=student)

# === API ===
@app.route('/generate_example', methods=['POST'])
def generate_example():
    data = request.get_json()
    class_num = int(data['class'])
    example_type = data['type']
    table_num = data.get('table_num', 'all')
    include_equation = data.get('include_equation')
    include_parentheses = data.get('include_parentheses')

    allowed_ops = {
        "addsub": ['+', '-'],
        "muldiv": ['*', '/'],
        "all": ['+', '-', '*', '/'],
        "+": ['+'],
        "-": ['-'],
        "*": ['*'],
        "/": ['/'],
    }.get(example_type, ['+', '-', '*', '/'])

    if class_num == 1:
        math = MathExamplesClass1(example_type, table_num)
        example = math.generate_example()
        correct = math.calculate_answer(example['a'], example['op'], example['b'])
        example['correct'] = correct
        return jsonify(example)
    elif class_num == 2:
        math = MathExamplesClass2(example_type, table_num)
        example = math.generate_example()
        correct = math.calculate_answer(example['a'], example['op'], example['b'])
        example['correct'] = correct
        return jsonify(example)
    else:
        math = MathExamplesClass3(example_type, table_num)
        options = ['default']
        if include_equation and any(op in allowed_ops for op in ['+', '-']):
            options.append('equation')
        if include_parentheses:
            # ВСЕГДА добавляем 'parentheses' — он теперь включает НОВЫЕ типы
            options.append('parentheses')
        selected = random.choice(options)
        if selected == 'equation':
            example = math.generate_simple_equation(allowed_ops=allowed_ops)
            example['correct'] = example['x']
            return jsonify(example)
        elif selected == 'parentheses':
            # Генерируем ЛЮБОЙ из трёх новых типов
            example = math.generate_parentheses_example(allowed_ops=allowed_ops)
            expr = example['expr']
            try:
                correct = eval(expr.replace(' ', ''))
            except Exception:
                correct = None
            example['correct'] = correct
            return jsonify(example)
        else:
            example = math.generate_example()
            correct = math.calculate_answer(example['a'], example['op'], example['b'])
            example['correct'] = correct
            return jsonify(example)


@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    class_num = int(data['class'])
    example_type = data['type']
    table_num = data.get('table_num', 'all')
    user_answer = data['answer']

    a = data.get('a')
    op = data.get('op')
    b = data.get('b')
    expr = data.get('expr', '')
    x_val = data.get('x')

    if x_val is not None and str(x_val).strip() != "":
        try:
            correct = int(x_val) if not isinstance(x_val, int) else x_val
            user_answer_num = int(user_answer)
        except Exception:
            return jsonify({'result': 'error', 'message': 'Введите число'})
        status = 'correct' if user_answer_num == correct else 'incorrect'
        return jsonify({'result': status, 'correct_answer': correct})

    if expr:
        try:
            correct = eval(expr.replace(' ', ''))
        except Exception:
            correct = None
        try:
            user_answer_num = int(user_answer)
        except Exception:
            return jsonify({'result': 'error', 'message': 'Введите число'})
        status = 'correct' if user_answer_num == correct else 'incorrect'
        return jsonify({'result': status, 'correct_answer': correct})

    if a is not None and op is not None and b is not None:
        if class_num == 1:
            math = MathExamplesClass1(example_type, table_num)
        elif class_num == 2:
            math = MathExamplesClass2(example_type, table_num)
        else:
            math = MathExamplesClass3(example_type, table_num)
        correct = math.calculate_answer(a, op, b)
        try:
            user_answer_num = int(user_answer)
        except Exception:
            return jsonify({'result': 'error', 'message': 'Введите число'})
        status = 'correct' if user_answer_num == correct else 'incorrect'
        return jsonify({'result': status, 'correct_answer': correct})

    return jsonify({'result': 'error', 'message': 'Ошибка формата примера'})

@app.route("/questions")
def questions():
    mode = request.args.get("mode", "all")
    if mode == "2":
        return jsonify(questions2)
    elif mode == "3":
        return jsonify(questions3)
    elif mode == "en_all":
        return jsonify(class2Words + class3Words)
    elif mode == "en_2":
        return jsonify(class2Words)
    elif mode == "en_3":
        return jsonify(class3Words)
    elif mode == "all":
        all_questions = {**questions2, **questions3}
        return jsonify(all_questions)
    return jsonify({})

# === РЕЗУЛЬТАТЫ ===
@app.route('/results/english')
def results_english():
    student = request.args.get('student', 'Арина')
    return render_template('results/english/results.html', student=student)

@app.route('/results/russian')
def results_russian():
    student = request.args.get('student', 'Арина')
    return render_template('results/russian/results.html', student=student)

@app.route('/results/math')
def results_math():
    student = request.args.get('student', 'Арина')
    return render_template('results/math/results.html', student=student)

# === ЗАПУСК СЕРВЕРА ===
def run_flask():
    app.run(debug=False, host='127.0.0.1', port=5000)

def open_browser():
    time.sleep(2)
    url = "http://127.0.0.1:5000"
    if sys.platform == "win32":
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        try:
            subprocess.Popen([chrome_path, "--new-window", url])
        except FileNotFoundError:
            subprocess.Popen(['cmd', '/c', 'start', '', url], shell=True)
    elif sys.platform == "darwin":
        subprocess.Popen(['open', '-n', '-a', 'Google Chrome', url])
    else:
        subprocess.Popen(['xdg-open', url])

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    open_browser()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass