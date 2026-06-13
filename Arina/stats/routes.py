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
    return render_template("diary/diary.html")


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


def normalize_grade_from_payload(data: dict) -> tuple[int | None, float | None, str | None]:
    """
    Возвращает:
    - grade: оценка 2–5, которую нужно сохранить в Google;
    - score_percent: процент, если он реально был передан;
    - error: текст ошибки, если данные некорректные.

    Поддерживает оба варианта:
    1. Новый правильный вариант:
       {"subject": "math", "score_percent": 80, "studentName": "Арина"}
       Тогда grade считается из процента.

    2. Текущий/старый вариант:
       {"subject": "math", "score_percent": 4, "studentName": "Арина"}
       Тогда 4 считается уже готовой оценкой.
    """
    if "grade" in data:
        try:
            grade = int(data["grade"])
        except (TypeError, ValueError):
            return None, None, "Поле grade должно быть числом от 2 до 5"

        if grade not in (2, 3, 4, 5):
            return None, None, "Поле grade должно быть числом от 2 до 5"

        score_percent = None
        if "score_percent" in data:
            try:
                score_percent = float(data["score_percent"])
                score_percent = max(0.0, min(score_percent, 100.0))
            except (TypeError, ValueError):
                score_percent = None

        return grade, score_percent, None

    if "score_percent" not in data:
        return None, None, "Требуется поле score_percent или grade"

    try:
        score_value = float(data["score_percent"])
    except (TypeError, ValueError):
        return None, None, "Поле score_percent должно быть числом"

    # ВАЖНО:
    # Если пришло 2/3/4/5 — считаем, что фронт отправил уже готовую оценку.
    # Это сохраняет совместимость с текущим поведением приложения.
    if score_value in (2, 3, 4, 5):
        return int(score_value), None, None

    # Иначе считаем, что пришёл процент правильных ответов.
    score_percent = max(0.0, min(score_value, 100.0))
    grade = percent_to_grade(score_percent)
    return grade, score_percent, None


@stats_bp.route("/stats")
@stats_bp.route("/diary")
def stats_page():
    """
    Страница дневника.

    Добавлены два URL:
    - /stats
    - /diary

    Потому что в меню сейчас ссылка ведёт именно на /diary.
    """
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
    """Сохранить результат в Google Таблицу."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON body is required"}), 400

    if "subject" not in data:
        return jsonify({"error": "Требуется поле subject"}), 400

    subject = str(data["subject"]).strip()

    if subject not in ("russian", "english", "math"):
        return jsonify({"error": "Поле subject должно быть russian, english или math"}), 400

    grade, score_percent, error = normalize_grade_from_payload(data)

    if error:
        return jsonify({"error": error}), 400

    student_name = str(data.get("studentName", DEFAULT_STUDENT)).strip() or DEFAULT_STUDENT

    # Google Apps Script сейчас ожидает поле score_percent,
    # но фактически сохраняет его как оценку.
    # Поэтому отправляем туда именно grade.
    payload = {
        "subject": subject,
        "score_percent": grade,
        "grade": grade,
        "studentName": student_name,
    }

    if score_percent is not None:
        payload["real_score_percent"] = score_percent

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
            return jsonify(
                {
                    "error": f"Google вернул статус {response.status_code}",
                    "raw_response": response.text[:500],
                }
            ), 502

        if not response.text.strip():
            return jsonify({"error": "Google вернул пустой ответ"}), 502

        try:
            google_data = response.json()
        except ValueError:
            return jsonify(
                {
                    "error": "Google вернул некорректный JSON",
                    "raw_response": response.text[:500],
                }
            ), 502

        # ВАЖНО:
        # Apps Script при ошибке возвращает HTTP 200, но внутри JSON кладёт error.
        # Раньше Flask это не проверял и отвечал status=saved.
        if isinstance(google_data, dict) and google_data.get("error"):
            return jsonify(
                {
                    "error": "Google Apps Script не сохранил результат",
                    "google_error": google_data.get("error"),
                    "sent_payload": payload,
                }
            ), 502

        return jsonify(
            {
                "status": "saved",
                "grade": grade,
                "score_percent": score_percent,
                "google_response": google_data,
            }
        )

    except requests.RequestException as e:
        return jsonify({"error": f"Ошибка запроса к Google: {e}"}), 502