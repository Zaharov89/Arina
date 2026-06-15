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


def get_topic_learning_content(topic_code: str, fallback_topics: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Return only learning content kept in code, not catalog metadata."""
    source = fallback_topics.get(topic_code, {})
    return {field: deepcopy(source.get(field, [] if field in {"rules", "examples"} else "")) for field in CONTENT_FIELDS}


def merge_db_topics_with_content(
    subject_code: str,
    class_number: int,
    fallback_topics: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Return topics keyed by topic code.

    Database is the source of catalog metadata: id, code, title, subject and class.
    Python topic files are kept only for learning content: description, rules and
    examples. If database is unavailable or empty, the old Python dictionaries are
    used as a full fallback so local development pages still open.
    """
    try:
        db_topics = get_topics_from_database(subject_code, class_number)
    except (RuntimeError, SQLAlchemyError, OSError):
        return deepcopy(fallback_topics)

    if not db_topics:
        return deepcopy(fallback_topics)

    merged_topics: dict[str, dict[str, Any]] = {}
    for db_topic in db_topics:
        topic_code = db_topic.get("code")
        if not topic_code:
            continue

        title = db_topic.get("title") or topic_code
        content_topic = get_topic_learning_content(topic_code, fallback_topics)
        content_topic.update(
            {
                "id": topic_code,
                "database_id": db_topic.get("id"),
                "code": topic_code,
                "title": title,
                "short_title": title,
                "subject_code": db_topic.get("subject_code", subject_code),
                "class_number": db_topic.get("class_number", class_number),
            }
        )
        merged_topics[topic_code] = content_topic

    return merged_topics or deepcopy(fallback_topics)


def build_topic_options(topics: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    """Build select options while keeping old template field names."""
    return [
        {
            "id": topic_code,
            "title": str(topic.get("title") or topic_code),
            "value": topic_code,
            "label": str(topic.get("title") or topic_code),
        }
        for topic_code, topic in topics.items()
    ]


def get_topic_or_none(
    subject_code: str,
    class_number: int,
    topic_id: str,
    fallback_topics: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    topics = merge_db_topics_with_content(subject_code, class_number, fallback_topics)
    return topics.get(topic_id)
