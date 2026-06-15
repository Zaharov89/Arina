from datetime import date
from decimal import Decimal
from typing import Any

from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import Date, cast, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from Arina.auth.services import AuthTokenError, get_token_user_id, decode_jwt_token
from Arina.database.models import Student, Subject, TestAnswer, TestAttempt, Topic, User
from Arina.database.session import get_session_factory

stats_bp = Blueprint("stats", __name__)

SUBJECT_TITLES = {
    "math": "Математика",
    "russian": "Русский язык",
    "world": "Окружающий мир",
    "english": "Английский язык",
}


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


def build_diary_empty_subject() -> dict:
    return {
        "month_avg": 0,
        "month_days": 0,
        "year_avg": 0,
        "year_days": 0,
        "grades": [],
    }


def build_diary_stats(session: Session, student: Student | None) -> dict:
    result = {subject_code: build_diary_empty_subject() for subject_code in SUBJECT_TITLES}
    if not student:
        return result

    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)

    for subject_code in SUBJECT_TITLES:
        subject = get_subject(session, subject_code)
        if not subject:
            continue

        base_filters = [TestAttempt.student_id == student.id, TestAttempt.subject_id == subject.id, TestAttempt.grade.is_not(None)]
        month_rows = session.execute(
            select(cast(TestAttempt.created_at, Date).label("grade_date"), func.max(TestAttempt.grade).label("grade"))
            .where(*base_filters, cast(TestAttempt.created_at, Date) >= month_start)
            .group_by(cast(TestAttempt.created_at, Date), TestAttempt.topic_id)
        ).all()
        year_rows = session.execute(
            select(cast(TestAttempt.created_at, Date).label("grade_date"), func.max(TestAttempt.grade).label("grade"))
            .where(*base_filters, cast(TestAttempt.created_at, Date) >= year_start)
            .group_by(cast(TestAttempt.created_at, Date), TestAttempt.topic_id)
        ).all()

        month_grades = [int(row.grade) for row in month_rows if row.grade is not None]
        year_grades = [int(row.grade) for row in year_rows if row.grade is not None]

        result[subject_code] = {
            "month_avg": round(sum(month_grades) / len(month_grades), 2) if month_grades else 0,
            "month_days": len({row.grade_date for row in month_rows}),
            "year_avg": round(sum(year_grades) / len(year_grades), 2) if year_grades else 0,
            "year_days": len({row.grade_date for row in year_rows}),
            "grades": [
                {
                    "date": str(row.grade_date),
                    "grade": int(row.grade),
                }
                for row in sorted(year_rows, key=lambda item: item.grade_date, reverse=True)
            ],
        }

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
        return f"Сегодня вы еще не проходили решали эту тему, ваша оценка {current_grade}"
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
