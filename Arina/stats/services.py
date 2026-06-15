from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from Arina.auth.services import AuthTokenError, decode_jwt_token, get_token_user_id
from Arina.database.session import get_session_factory
from Arina.stats.repositories import StatsRepository
from Arina.stats.schemas import TestAttemptPayload, parse_test_attempt_payload
from Arina.math.class_1_topics import MATH_CLASS_1_TOPICS
from Arina.math.class_2_topics import MATH_CLASS_2_TOPICS
from Arina.math.class_3_topics import MATH_CLASS_3_TOPICS
from Arina.russian_language.class_1_topics import RUSSIAN_CLASS_1_TOPICS
from Arina.russian_language.class_2_topics import RUSSIAN_CLASS_2_TOPICS
from Arina.russian_language.class_3_topics import RUSSIAN_CLASS_3_TOPICS
from Arina.world.class_1_topics import WORLD_CLASS_1_TOPICS
from Arina.world.class_2_topics import WORLD_CLASS_2_TOPICS
from Arina.world.class_3_topics import WORLD_CLASS_3_TOPICS
from Arina.english_language.class_2_topics import ENGLISH_CLASS_2_TOPICS
from Arina.english_language.class_3_topics import ENGLISH_CLASS_3_TOPICS

SUBJECT_TITLES = {"math": "Математика", "russian": "Русский язык", "world": "Окружающий мир", "english": "Английский язык"}
SUBJECT_ORDER = ["math", "russian", "world", "english"]
CONTROL_SLICE_CODE = "control_slice"
CONTROL_SLICE_TITLE = "Контрольный срез"

TOPIC_FALLBACKS = {
    "math": {1: MATH_CLASS_1_TOPICS, 2: MATH_CLASS_2_TOPICS, 3: MATH_CLASS_3_TOPICS},
    "russian": {1: RUSSIAN_CLASS_1_TOPICS, 2: RUSSIAN_CLASS_2_TOPICS, 3: RUSSIAN_CLASS_3_TOPICS},
    "world": {1: WORLD_CLASS_1_TOPICS, 2: WORLD_CLASS_2_TOPICS, 3: WORLD_CLASS_3_TOPICS},
    "english": {2: ENGLISH_CLASS_2_TOPICS, 3: ENGLISH_CLASS_3_TOPICS},
}


def get_user_id_from_access_token(access_token: str) -> int:
    payload = decode_jwt_token(access_token, expected_type="access")
    return get_token_user_id(payload)


def get_current_user(repository: StatsRepository, user_id: int):
    user = repository.get_user(user_id)
    if not user or not user.is_active:
        raise AuthTokenError("Пользователь не авторизован.")
    return user


def calculate_grade(score_percent: int | float | Decimal) -> int:
    score = float(score_percent or 0)
    error_percent = 100 - score
    if error_percent <= 5: return 5
    if error_percent <= 15: return 4
    if error_percent <= 30: return 3
    return 2


def get_month_dates(today: date) -> list[str]:
    return [str(date(today.year, today.month, day)) for day in range(1, today.day + 1)]


def build_empty_subject(subject_code: str, title: str) -> dict:
    return {"code": subject_code, "title": title, "month_avg": 0, "month_days": 0, "year_avg": 0, "year_days": 0, "topics": [], "grades": []}


def get_topic_code(row) -> str:
    return row.topic_code or "general"


def get_topic_title(row) -> str:
    if row.topic_code == CONTROL_SLICE_CODE:
        return CONTROL_SLICE_TITLE
    return row.topic_title or "Общий тест"


def fallback_title(topic_code: str, topic_data: dict) -> str:
    return topic_data.get("title") or topic_data.get("short_title") or topic_data.get("description") or topic_code.replace("_", " ").capitalize()


def merge_topics_with_code_fallbacks(subject_code: str, db_topics: list) -> list:
    merged = list(db_topics)
    existing = {(topic.class_number, topic.code) for topic in merged}
    fake_id = -1
    for class_number, topics in TOPIC_FALLBACKS.get(subject_code, {}).items():
        for topic_code, topic_data in topics.items():
            if (class_number, topic_code) in existing:
                continue
            merged.append(SimpleNamespace(id=f"fallback-{subject_code}-{class_number}-{topic_code}", code=topic_code, title=fallback_title(topic_code, topic_data), class_number=class_number, is_active=True))
            fake_id -= 1
    return merged


def format_grade_row(row) -> dict:
    return {"date": str(row.grade_date), "grade": int(row.grade), "topic_id": row.topic_id, "topic_code": get_topic_code(row), "topic_title": get_topic_title(row)}


def build_topic_diary(topics: list, month_rows: list) -> list[dict]:
    topic_map: dict[int | str | None, dict] = {}
    for topic in topics:
        topic_map[topic.id] = {"topic_id": topic.id, "topic_code": topic.code, "topic_title": topic.title, "class_number": topic.class_number, "month_grades": [], "month_avg": 0, "best_grade": None, "last_grade": None, "last_date": None, "is_control_slice": topic.code == CONTROL_SLICE_CODE}
    for row in month_rows:
        topic_id = row.topic_id
        topic_code = get_topic_code(row)
        topic_title = get_topic_title(row)
        if topic_id not in topic_map:
            topic_map[topic_id] = {"topic_id": topic_id, "topic_code": topic_code, "topic_title": topic_title, "class_number": getattr(row, "class_number", None), "month_grades": [], "month_avg": 0, "best_grade": None, "last_grade": None, "last_date": None, "is_control_slice": topic_code == CONTROL_SLICE_CODE}
        grade_item = {"date": str(row.grade_date), "grade": int(row.grade)}
        topic_map[topic_id]["month_grades"].append(grade_item)
    for topic in topic_map.values():
        grades = [item["grade"] for item in topic["month_grades"]]
        if grades:
            topic["month_avg"] = round(sum(grades) / len(grades), 2)
            topic["best_grade"] = max(grades)
            topic["last_grade"] = topic["month_grades"][0]["grade"]
            topic["last_date"] = topic["month_grades"][0]["date"]
    return sorted(topic_map.values(), key=lambda item: (item.get("class_number") or 99, 1 if item.get("is_control_slice") else 0, item["topic_title"]))


def build_diary_stats(repository: StatsRepository, student) -> dict:
    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    result = {"server_date": str(today), "month_dates": get_month_dates(today), "subjects": []}
    for subject_code in SUBJECT_ORDER:
        subject = repository.get_subject(subject_code)
        title = SUBJECT_TITLES.get(subject_code, subject_code)
        subject_data = build_empty_subject(subject_code, title)
        if subject and student:
            topics = merge_topics_with_code_fallbacks(subject_code, repository.get_subject_topics(subject))
            month_rows = repository.get_grade_rows(student, subject, month_start)
            year_rows = repository.get_grade_rows(student, subject, year_start)
            month_grades = [int(row.grade) for row in month_rows if row.grade is not None]
            year_grades = [int(row.grade) for row in year_rows if row.grade is not None]
            subject_data.update({"month_avg": round(sum(month_grades) / len(month_grades), 2) if month_grades else 0, "month_days": len({row.grade_date for row in month_rows}), "year_avg": round(sum(year_grades) / len(year_grades), 2) if year_grades else 0, "year_days": len({row.grade_date for row in year_rows}), "topics": build_topic_diary(topics, month_rows), "grades": [format_grade_row(row) for row in year_rows]})
        result[subject_code] = subject_data
        result["subjects"].append(subject_data)
    return result


def get_diary_stats(access_token: str) -> dict:
    user_id = get_user_id_from_access_token(access_token)
    session_factory = get_session_factory()
    with session_factory() as session:
        repository = StatsRepository(session)
        user = get_current_user(repository, user_id)
        student = repository.get_student_by_user_id(user.id)
        return build_diary_stats(repository, student)


def build_save_message(previous_grade: int | None, current_grade: int, action: str) -> str:
    if action == "created": return f"Сегодня вы еще не решали эту тему, ваша оценка {current_grade}"
    if action == "improved": return f"Ваша прошлая оценка {previous_grade}, сейчас получили {current_grade}, поздравляем, Вы исправили оценку!"
    if action == "same": return f"Ваша прошлая оценка {previous_grade}, сейчас получили {current_grade}, оценка не изменилась"
    return f"Ваша прошлая оценка {previous_grade}, сейчас получили {current_grade}, предыдущую оценку не исправляем"


def resolve_attempt_topic(repository: StatsRepository, subject, payload: TestAttemptPayload):
    if payload.topic_code == CONTROL_SLICE_CODE:
        return repository.get_or_create_inactive_topic(subject, payload.class_number, CONTROL_SLICE_CODE, CONTROL_SLICE_TITLE)
    return repository.get_topic(subject, payload.class_number, payload.topic_code)


def save_test_attempt(access_token: str, raw_payload) -> tuple[dict, int]:
    payload = parse_test_attempt_payload(raw_payload)
    user_id = get_user_id_from_access_token(access_token)
    session_factory = get_session_factory()
    with session_factory() as session:
        repository = StatsRepository(session)
        user = get_current_user(repository, user_id)
        student = repository.get_student_by_user_id(user.id)
        if not student: return {"status": "not_found", "message": "У пользователя нет ученика."}, 404
        subject = repository.get_subject(payload.subject_code)
        if not subject: return {"status": "validation_error", "message": "Предмет не найден."}, 400
        topic = resolve_attempt_topic(repository, subject, payload)
        grade = calculate_grade(payload.score_percent)
        existing = repository.find_today_attempt(student.id, subject.id, topic.id if topic else None)
        previous_grade = existing.grade if existing else None
        if existing is None:
            attempt = repository.create_attempt(student.id, subject.id, payload.class_number, topic.id if topic else None, payload.total_questions, payload.correct_answers, payload.wrong_answers, payload.empty_answers, payload.score_percent, grade, payload.time_spent_seconds, payload.average_time_seconds)
            repository.replace_attempt_answers(attempt, payload.answers)
            action = "created"
        elif grade > (existing.grade or 0):
            repository.update_attempt(existing, payload.class_number, payload.total_questions, payload.correct_answers, payload.wrong_answers, payload.empty_answers, payload.score_percent, grade, payload.time_spent_seconds, payload.average_time_seconds)
            repository.replace_attempt_answers(existing, payload.answers)
            action = "improved"
        elif grade == existing.grade:
            action = "same"
        else:
            action = "lower"
        session.commit()
        return {"status": "ok", "action": action, "previous_grade": previous_grade, "current_grade": grade, "saved_grade": grade if action in {"created", "improved"} else previous_grade, "message": build_save_message(previous_grade, grade, action)}, 200
