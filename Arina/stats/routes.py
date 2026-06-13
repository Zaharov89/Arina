import os

import requests
from flask import Blueprint, jsonify, render_template, request

try:
    from Arina.config import DEFAULT_STUDENT, GOOGLE_SCRIPT_URL
except ImportError:
    DEFAULT_STUDENT = "Арина"
    GOOGLE_SCRIPT_URL = os.getenv(
        "ARINA_GOOGLE_SCRIPT_URL",
        "https://script.google.com/macros/s/AKfycbx65oYhyhhQYIQIacWb-ZXgfEpISmHQLdCBPcRZLWSPoT9WnEBZ9uxnwt_7HyXgqCo/exec",
    )


current_dir = os.path.dirname(os.path.abspath(__file__))
template_folder = os.path.join(current_dir, "..", "templates")
static_folder = os.path.join(current_dir, "..", "static")

stats_bp = Blueprint(
    "stats",
    __name__,
    template_folder=template_folder,
    static_folder=static_folder,
)


@stats_bp.route("/stats")
@stats_bp.route("/diary")
def stats_page():
    """Страница дневника."""
    return render_template("diary/diary.html")


def get_student_name_from_args() -> str:
    student_name = request.args.get("student", DEFAULT_STUDENT)
    return student_name.strip() or DEFAULT_STUDENT


@stats_bp.route("/api/stats")
def api_get_stats():
    """Получить статистику из Google Таблицы для отображения дневника."""
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
            return jsonify(
                {
                    "error": f"Google вернул статус {response.status_code}",
                    "raw_response": response.text[:500],
                }
            ), 502

        if not response.text.strip():
            return jsonify({"error": f"Google вернул пустой ответ для ученика {student_name}"}), 502

        try:
            data = response.json()
        except ValueError:
            return jsonify(
                {
                    "error": "Google вернул некорректный JSON",
                    "raw_response": response.text[:500],
                }
            ), 502

        if isinstance(data, dict) and data.get("error"):
            return jsonify(
                {
                    "error": "Google Apps Script вернул ошибку",
                    "google_error": data.get("error"),
                }
            ), 502

        return jsonify(data)

    except requests.RequestException as e:
        return jsonify({"error": f"Ошибка запроса к Google: {e}"}), 502


@stats_bp.route("/api/save_result", methods=["POST"])
def api_save_result():
    """
    Временная заглушка сохранения результатов.

    Сохранение в Google откладываем. В будущем этот endpoint будет заменён
    на сохранение результата в PostgreSQL через полноценный REST API.
    Заглушка нужна, чтобы старые fetch-запросы с фронта не ломали страницу
    результатов, если где-то автосохранение ещё осталось включённым.
    """
    data = request.get_json(silent=True)

    return jsonify(
        {
            "status": "disabled",
            "message": "Сохранение результатов временно отключено. Позже будет PostgreSQL.",
            "received_payload": data if isinstance(data, dict) else None,
        }
    ), 200
