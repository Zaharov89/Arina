from copy import deepcopy
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from Arina.database.repositories import ReferenceDataRepository
from Arina.database.session import get_session_factory

CONTENT_FIELDS = ("description", "rules", "examples")


def get_topics_from_database(subject_code: str, class_number: int) -> list[dict]:
    session_factory = get_session_factory()
    with session_factory() as session:
        return ReferenceDataRepository(session).get_topics(subject_code=subject_code, class_number=class_number)


def humanize_topic_code(topic_code: str) -> str:
    return topic_code.replace("_", " ").strip().capitalize()


def normalize_fallback_topics(fallback_topics: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    topics = deepcopy(fallback_topics)
    for topic_code, topic in topics.items():
        title = topic.get("title") or topic.get("short_title") or topic.get("description") or humanize_topic_code(topic_code)
        topic.setdefault("id", topic_code)
        topic.setdefault("code", topic_code)
        topic["title"] = title
        topic.setdefault("short_title", title)
        topic.setdefault("description", "")
        topic.setdefault("rules", [])
        topic.setdefault("examples", [])
    return topics


def get_topic_learning_content(topic_code: str, fallback_topics: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source = fallback_topics.get(topic_code, {})
    return {field: deepcopy(source.get(field, [] if field in {"rules", "examples"} else "")) for field in CONTENT_FIELDS}


def merge_db_topics_with_content(subject_code: str, class_number: int, fallback_topics: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    try:
        db_topics = get_topics_from_database(subject_code, class_number)
    except (RuntimeError, SQLAlchemyError, OSError):
        return normalize_fallback_topics(fallback_topics)

    if not db_topics:
        return normalize_fallback_topics(fallback_topics)

    merged_topics: dict[str, dict[str, Any]] = {}
    for db_topic in db_topics:
        topic_code = db_topic.get("code")
        if not topic_code:
            continue
        title = db_topic.get("title") or humanize_topic_code(topic_code)
        content_topic = get_topic_learning_content(topic_code, fallback_topics)
        content_topic.update({"id": topic_code, "database_id": db_topic.get("id"), "code": topic_code, "title": title, "short_title": title, "subject_code": db_topic.get("subject_code", subject_code), "class_number": db_topic.get("class_number", class_number)})
        merged_topics[topic_code] = content_topic

    return merged_topics or normalize_fallback_topics(fallback_topics)


def build_topic_options(topics: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    return [{"id": topic_code, "title": str(topic.get("title") or topic.get("description") or humanize_topic_code(topic_code)), "value": topic_code, "label": str(topic.get("title") or topic.get("description") or humanize_topic_code(topic_code))} for topic_code, topic in topics.items()]


def get_topic_or_none(subject_code: str, class_number: int, topic_id: str, fallback_topics: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    topics = merge_db_topics_with_content(subject_code, class_number, fallback_topics)
    return topics.get(topic_id)
