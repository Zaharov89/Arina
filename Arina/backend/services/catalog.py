from copy import deepcopy
from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from Arina.database.repositories import ReferenceDataRepository
from Arina.database.session import get_session_factory


def get_topics_from_database(subject_code: str, class_number: int) -> list[dict]:
    session_factory = get_session_factory()
    with session_factory() as session:
        return ReferenceDataRepository(session).get_topics(subject_code=subject_code, class_number=class_number)


def merge_db_topics_with_content(
    subject_code: str,
    class_number: int,
    fallback_topics: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """
    Return topics keyed by topic code.

    Current database stores topic identity and title. Learning content such as
    descriptions, rules and examples is still kept in Python generators/content
    files, so this function safely overlays database title/code over existing
    content. If database is unavailable or empty, it falls back to old data.
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

        content_topic = deepcopy(fallback_topics.get(topic_code, {}))
        title = db_topic.get("title") or content_topic.get("title") or topic_code
        content_topic.update(
            {
                "id": db_topic.get("id"),
                "code": topic_code,
                "title": title,
                "short_title": content_topic.get("short_title") or title,
                "subject_code": db_topic.get("subject_code", subject_code),
                "class_number": db_topic.get("class_number", class_number),
            }
        )
        content_topic.setdefault("description", "")
        content_topic.setdefault("rules", [])
        content_topic.setdefault("examples", [])
        merged_topics[topic_code] = content_topic

    return merged_topics or deepcopy(fallback_topics)


def build_topic_options(topics: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "value": topic_code,
            "label": str(topic.get("short_title") or topic.get("title") or topic_code),
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
