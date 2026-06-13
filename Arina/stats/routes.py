import os

import requests
from flask import Blueprint, jsonify, render_template, request

try:
    from Arina.config import DEFAULT_STUDENT, GOOGLE_SCRIPT_URL
except ImportError:
    DEFAULT_STUDENT = "Арина"
    GOOGLE_SCRIPT_URL = os.getenv(
        "ARINA_GOOGLE_SCRIPT_URL",
        "https://script.google.com/macros/s/AKfycbwSw2z5nGJ-GQhtCzkYM8cKLy8WOFM47IyY0ahUi3JJDe1y-m4vZKOW_mnzCnMk3Dm7/exec",
    )


current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, "..", "templates", "stats")
static_folder = os.path.join(current_dir, "..", "static")

stats_bp = Blueprint(
    "stats",
    __name__,
    template_folder=template_folder,
    static_folder=static_folder,
)


def percent_to_grade(percent_correct: float) -> int:
    """Конвертирует процент правильных ответов в школьную оценку 2–5."""
    percent_errors = 100.0 - percent_correct

    if percent_errors <= 5:
        return 5

    if percent_errors <= 15:
        return 4

    if percent_errors <= 30:
        return 3

    return 2


def get_student_name_from_args() -> str:
    student_name = request.args.get("student", DEFAULT_STUDENT)
    return student_name.strip() or DEFAULT_STUDENT


@stats_bp.route("/stats")
def stats_page():
    """Страница дневника."""
    return render_template("stats.html")


@stats_bp.route("/api/stats")
def api_get_stats():
    """Получить статистику из Google Таблицы."""
    student_name = get_student_name_from_args()

    try:
        response = requests.get(
            GOOGLE_SCRIPT_URL,
            params={
                "path": "get_stats",
                "studentName": student_name,
            },
            timeout=10,
        )

        if response.status_code != 200:
            return jsonify({"error": f"Google вернул статус {response.status_code}"}), 502

        if not response.text.strip():
            return jsonify({"error": f"Google вернул пустой ответ для ученика {student_name}"}), 502

        try:
            data = response.json()
        except ValueError:
            return jsonify({"error": "Google вернул некорректный JSON"}), 502

        return jsonify(data)

    except requests.RequestException as e:
        return jsonify({"error": f"Ошибка запроса к Google: {e}"}), 502


@stats_bp.route("/api/save_result", methods=["POST"])
def api_save_result():
    """Сохранить результат в Google Таблицу."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON body is required"}), 400

    if "subject" not in data or "score_percent" not in data:
        return jsonify({"error": "Требуются поля: subject, score_percent"}), 400

    subject = str(data["subject"]).strip()

    if not subject:
        return jsonify({"error": "Поле subject не может быть пустым"}), 400

    try:
        score_percent = float(data["score_percent"])
    except (TypeError, ValueError):
        return jsonify({"error": "Поле score_percent должно быть числом"}), 400

    score_percent = max(0.0, min(score_percent, 100.0))
    grade = percent_to_grade(score_percent)

    student_name = str(data.get("studentName", DEFAULT_STUDENT)).strip() or DEFAULT_STUDENT

    payload = {
        "subject": subject,
        "score_percent": score_percent,
        "grade": grade,
        "studentName": student_name,
    }

    try:
        response = requests.post(
            GOOGLE_SCRIPT_URL,
            params={
                "path": "arina_stats",
            },
            json=payload,
            headers={
                "Content-Type": "application/json",
            },
            timeout=10,
        )

        if response.status_code != 200:
            return jsonify({"error": f"Google вернул статус {response.status_code}"}), 502

        return jsonify(
            {
                "status": "saved",
                "score_percent": score_percent,
                "grade": grade,
            }
        )

    except requests.RequestException as e:
        return jsonify({"error": f"Ошибка запроса к Google: {e}"}), 502