from flask import Blueprint, render_template, jsonify, request
import requests
import os

# УБРАНЫ ЛИШНИЕ ПРОБЕЛЫ В КОНЦЕ URL
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbwSw2z5nGJ-GQhtCzkYM8cKLy8WOFM47IyY0ahUi3JJDe1y-m4vZKOW_mnzCnMk3Dm7/exec"

# Определяем путь к шаблонам относительно текущего файла
current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, '..', 'templates', 'stats')
static_folder = os.path.join(current_dir, '..', 'static')

stats_bp = Blueprint('stats', __name__,
                     template_folder=template_folder,
                     static_folder=static_folder)

def percent_to_grade(percent_correct: float) -> int:
    """Конвертирует процент ПРАВИЛЬНЫХ ответов в школьную оценку (2–5)"""
    percent_errors = 100.0 - percent_correct
    if percent_errors <= 5:
        return 5
    elif percent_errors <= 15:
        return 4
    elif percent_errors <= 30:
        return 3
    else:
        return 2

@stats_bp.route('/stats')
def stats_page():
    """Страница дневника"""
    return render_template('stats.html')

@stats_bp.route('/api/stats')
def api_get_stats():
    """Получить статистику из Google Таблицы"""
    student_name = request.args.get("student")
    if not student_name:
        return jsonify({"error": "Не указан ученик (параметр 'student')"}), 400

    try:
        response = requests.get(
            f"{WEB_APP_URL}?path=get_stats&studentName={student_name}",
            timeout=10
        )
        if response.status_code != 200:
            return jsonify({"error": f"Google вернул статус {response.status_code}"}), 500
        if not response.text.strip():
            return jsonify({"error": f"Google вернул пустой ответ для ученика {student_name}"}), 500
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@stats_bp.route('/api/save_result', methods=['POST'])
def api_save_result():
    """Сохранить результат в Google Таблицу"""
    try:
        data = request.get_json()
        if not data or "subject" not in data or "score_percent" not in data:
            return jsonify({"error": "Требуются поля: subject, score_percent"}), 400

        student_name = data.get("studentName", "Арина")
        grade = percent_to_grade(float(data["score_percent"]))

        payload = {
            "subject": data["subject"],
            "score_percent": grade,
            "studentName": student_name
        }

        response = requests.post(
            f"{WEB_APP_URL}?path=arina_stats",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code != 200:
            return jsonify({"error": f"Google вернул статус {response.status_code}"}), 500

        return jsonify({"status": "saved", "grade": grade})
    except Exception as e:
        return jsonify({"error": str(e)}), 500