from datetime import date
from decimal import Decimal
from typing import Any

from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import Date, cast, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from Arina.auth.services import AuthTokenError, decode_jwt_token, get_token_user_id
from Arina.database.models import Student, Subject, TestAnswer, TestAttempt, Topic, User
from Arina.database.session import get_session_factory

stats_bp = Blueprint("stats", __name__)

SUBJECT_TITLES = {
    "math": "Математика",
    "russian": "Русский язык",
    "world": "Окружающий мир",
    "english": "Английский язык",
}

SUBJECT_ORDER = ["math", "russian", "world", "english"]


def get_access_token_from_request() -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return ""


def get_current_user(session: Session) -> User:
    payload = decode_jwt_token(get_access_token_from_request(), expected_type="access")
    user = session.get(User, get_token_user_id(payload))
    if not user or not user.is_active:
        raise AuthTokenError("Пользователь не авторизован.")
    return user


def get_current_student(session: Session, user: User) -> Student | None:
    return session.scalar(select(Student).where(Student.user_id == user.id).order_by(Student.id).limit(1))


def calculate_grade(score_percent: int | float | Decimal) -> int:
    score = float(score_percent or 0)
    error_percent = 100 - score
    if error_percent <= 5:
        return 5
    if error_percent <= 15:
        return 4
    if error_percent <= 30:
        return 3
    return 2


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def to_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        return default


def get_subject(session: Session, subject_code: str) -> Subject | None:
    return session.scalar(select(Subject).where(Subject.code == subject_code))


def get_topic(session: Session, subject: Subject, class_number: int, topic_code: str | None) -> Topic | None:
    if not topic_code:
        return None
    return session.scalar(
        select(Topic).where(
            Topic.subject_id == subject.id,
            Topic.class_number == class_number,
            Topic.code == topic_code,
        )
    )


def get_month_dates(today: date) -> list[str]:
    return [str(date(today.year, today.month, day)) for day in range(1, today.day + 1)]


def build_empty_subject(subject_code: str, title: str) -> dict:
    return {
        "code": subject_code,
        "title": title,
        "month_avg": 0,
        "month_days": 0,
        "year_avg": 0,
        "year_days": 0,
        "topics": [],
        "grades": [],
    }


def format_grade_row(row) -> dict:
    return {
        "date": str(row.grade_date),
        "grade": int(row.grade),
        "topic_id": row.topic_id,
        "topic_code": row.topic_code or "general",
        "topic_title": row.topic_title or "Общий тест",
    }


def get_subject_topics(session: Session, subject: Subject) -> list[Topic]:
    return list(
        session.scalars(
            select(Topic)
            .where(Topic.subject_id == subject.id, Topic.is_active.is_(True))
            .order_by(Topic.class_number, Topic.id)
        ).all()
    )


def get_grade_rows(session: Session, student: Student, subject: Subject, start_date: date):
    return session.execute(
        select(
            cast(TestAttempt.created_at, Date).label("grade_date"),
            TestAttempt.topic_id.label("topic_id"),
            Topic.code.label("topic_code"),
            Topic.title.label("topic_title"),
            func.max(TestAttempt.grade).label("grade"),
        )
        .select_from(TestAttempt)
        .outerjoin(Topic, TestAttempt.topic_id == Topic.id)
        .where(
            TestAttempt.student_id == student.id,
            TestAttempt.subject_id == subject.id,
            TestAttempt.grade.is_not(None),
            cast(TestAttempt.created_at, Date) >= start_date,
        )
        .group_by(cast(TestAttempt.created_at, Date), TestAttempt.topic_id, Topic.code, Topic.title)
        .order_by(cast(TestAttempt.created_at, Date).desc(), Topic.title)
    ).all()


def build_topic_diary(topics: list[Topic], month_rows: list) -> list[dict]:
    topic_map: dict[int | None, dict] = {}

    for topic in topics:
        topic_map[topic.id] = {
            "topic_id": topic.id,
            "topic_code": topic.code,
            "topic_title": topic.title,
            "class_number": topic.class_number,
            "month_grades": [],
            "month_avg": 0,
            "best_grade": None,
            "last_grade": None,
            "last_date": None,
        }

    for row in month_rows:
        topic_id = row.topic_id
        if topic_id not in topic_map:
            topic_map[topic_id] = {
                "topic_id": topic_id,
                "topic_code": row.topic_code or "general",
                "topic_title": row.topic_title or "Общий тест",
                "class_number": None,
                "month_grades": [],
                "month_avg": 0,
                "best_grade": None,
                "last_grade": None,
                "last_date": None,
            }

        grade_item = {"date": str(row.grade_date), "grade": int(row.grade)}
        topic_map[topic_id]["month_grades"].append(grade_item)

    for topic in topic_map.values():
        grades = [item["grade"] for item in topic["month_grades"]]
        if grades:
            topic["month_avg"] = round(sum(grades) / len(grades), 2)
            topic["best_grade"] = max(grades)
            topic["last_grade"] = topic["month_grades"][0]["grade"]
            topic["last_date"] = topic["month_grades"][0]["date"]

    return sorted(topic_map.values(), key=lambda item: (item.get("class_number") or 99, item["topic_title"]))


def build_diary_stats(session: Session, student: Student | None) -> dict:
    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    result = {
        "server_date": str(today),
        "month_dates": get_month_dates(today),
        "subjects": [],
    }

    for subject_code in SUBJECT_ORDER:
        subject = get_subject(session, subject_code)
        title = SUBJECT_TITLES.get(subject_code, subject_code)
        subject_data = build_empty_subject(subject_code, title)

        if subject and student:
            topics = get_subject_topics(session, subject)
            month_rows = get_grade_rows(session, student, subject, month_start)
            year_rows = get_grade_rows(session, student, subject, year_start)
            month_grades = [int(row.grade) for row in month_rows if row.grade is not None]
            year_grades = [int(row.grade) for row in year_rows if row.grade is not None]

            subject_data.update(
                {
                    "month_avg": round(sum(month_grades) / len(month_grades), 2) if month_grades else 0,
                    "month_days": len({row.grade_date for row in month_rows}),
                    "year_avg": round(sum(year_grades) / len(year_grades), 2) if year_grades else 0,
                    "year_days": len({row.grade_date for row in year_rows}),
                    "topics": build_topic_diary(topics, month_rows),
                    "grades": [format_grade_row(row) for row in year_rows],
                }
            )

        result[subject_code] = subject_data
        result["subjects"].append(subject_data)

    return result


def find_today_attempt(session: Session, student_id: int, subject_id: int, topic_id: int | None) -> TestAttempt | None:
    today = date.today()
    query = select(TestAttempt).where(
        TestAttempt.student_id == student_id,
        TestAttempt.subject_id == subject_id,
        cast(TestAttempt.created_at, Date) == today,
    )
    if topic_id is None:
        query = query.where(TestAttempt.topic_id.is_(None))
    else:
        query = query.where(TestAttempt.topic_id == topic_id)

    return session.scalar(query.order_by(TestAttempt.created_at.desc()).limit(1))


def replace_attempt_answers(session: Session, attempt: TestAttempt, answers: list[dict]) -> None:
    session.query(TestAnswer).filter(TestAnswer.attempt_id == attempt.id).delete(synchronize_session=False)
    for answer in answers:
        question_text = str(answer.get("question") or answer.get("question_text") or answer.get("example") or "Задание")
        session.add(
            TestAnswer(
                attempt_id=attempt.id,
                question_text=question_text,
                user_answer=None if answer.get("userAnswer") is None else str(answer.get("userAnswer")),
                correct_answer=None if answer.get("correctAnswer") is None else str(answer.get("correctAnswer")),
                is_correct=bool(answer.get("is_correct", False)),
                answer_type=answer.get("answer_type"),
            )
        )


def build_save_message(previous_grade: int | None, current_grade: int, action: str) -> str:
    if action == "created":
        return f"Сегодня вы еще не решали эту тему, ваша оценка {current_grade}"
    if action == "improved":
        return f"Ваша прошлая оценка {previous_grade}, сейчас получили {current_grade}, поздравляем, Вы исправили оценку!"
    if action == "same":
        return f"Ваша прошлая оценка {previous_grade}, сейчас получили {current_grade}, оценка не изменилась"
    return f"Ваша прошлая оценка {previous_grade}, сейчас получили {current_grade}, предыдущую оценку не исправляем"


@stats_bp.route("/stats")
@stats_bp.route("/diary")
def stats_page():
    return render_template("diary/diary.html")


@stats_bp.route("/api/stats")
def api_get_stats():
    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            user = get_current_user(session)
            student = get_current_student(session, user)
            data = build_diary_stats(session, student)
            return jsonify(data)
    except AuthTokenError as error:
        return jsonify({"error": str(error), "status": "unauthorized"}), 401
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify({"error": f"Ошибка чтения дневника из PostgreSQL: {error}"}), 500


@stats_bp.route("/api/test-attempts", methods=["POST"])
def api_save_test_attempt():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"status": "validation_error", "message": "JSON body is required"}), 400

    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            user = get_current_user(session)
            student = get_current_student(session, user)
            if not student:
                return jsonify({"status": "not_found", "message": "У пользователя нет ученика."}), 404

            subject_code = str(payload.get("subject_code") or payload.get("subject") or "").strip()
            subject = get_subject(session, subject_code)
            if not subject:
                return jsonify({"status": "validation_error", "message": "Предмет не найден."}), 400

            class_number = to_int(payload.get("class_number"), 1)
            topic_code = str(payload.get("topic_code") or "").strip() or None
            topic = get_topic(session, subject, class_number, topic_code)

            total_questions = max(0, to_int(payload.get("total_questions"), 0))
            correct_answers = max(0, to_int(payload.get("correct_answers"), 0))
            wrong_answers = max(0, to_int(payload.get("wrong_answers"), 0))
            empty_answers = max(0, to_int(payload.get("empty_answers"), 0))
            score_percent = to_decimal(payload.get("score_percent"), Decimal("0"))
            grade = calculate_grade(score_percent)
            time_spent_seconds = max(0, to_int(payload.get("time_spent_seconds"), 0))
            average_time_seconds = to_decimal(payload.get("average_time_seconds"), Decimal("0"))
            answers = payload.get("answers") if isinstance(payload.get("answers"), list) else []

            existing = find_today_attempt(session, student.id, subject.id, topic.id if topic else None)
            previous_grade = existing.grade if existing else None

            if existing is None:
                attempt = TestAttempt(
                    student_id=student.id,
                    subject_id=subject.id,
                    class_number=class_number,
                    topic_id=topic.id if topic else None,
                    total_questions=total_questions,
                    correct_answers=correct_answers,
                    wrong_answers=wrong_answers,
                    empty_answers=empty_answers,
                    score_percent=score_percent,
                    grade=grade,
                    time_spent_seconds=time_spent_seconds,
                    average_time_seconds=average_time_seconds,
                )
                session.add(attempt)
                session.flush()
                replace_attempt_answers(session, attempt, answers)
                action = "created"
            elif grade > (existing.grade or 0):
                existing.class_number = class_number
                existing.total_questions = total_questions
                existing.correct_answers = correct_answers
                existing.wrong_answers = wrong_answers
                existing.empty_answers = empty_answers
                existing.score_percent = score_percent
                existing.grade = grade
                existing.time_spent_seconds = time_spent_seconds
                existing.average_time_seconds = average_time_seconds
                replace_attempt_answers(session, existing, answers)
                action = "improved"
            elif grade == existing.grade:
                action = "same"
            else:
                action = "lower"

            session.commit()
            return jsonify(
                {
                    "status": "ok",
                    "action": action,
                    "previous_grade": previous_grade,
                    "current_grade": grade,
                    "saved_grade": grade if action in {"created", "improved"} else previous_grade,
                    "message": build_save_message(previous_grade, grade, action),
                }
            )
    except AuthTokenError as error:
        return jsonify({"status": "unauthorized", "message": str(error)}), 401
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify({"status": "error", "message": f"Не удалось сохранить результат в PostgreSQL: {error}"}), 500


@stats_bp.route("/api/save_result", methods=["POST"])
def api_save_result_legacy():
    return api_save_test_attempt()
