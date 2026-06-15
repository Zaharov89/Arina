from sqlalchemy import text
from sqlalchemy.orm import Session


RUSSIAN_VOCABULARY_SELECT = text(
    """
    SELECT id, class_number, word, answer, is_active
    FROM arina.russian_vocabulary_words
    WHERE is_active = true
      AND (:class_number IS NULL OR class_number = :class_number)
    ORDER BY class_number, word
    """
)


def get_russian_vocabulary_words(session: Session, class_number: int | None = None) -> list[dict]:
    rows = session.execute(RUSSIAN_VOCABULARY_SELECT, {"class_number": class_number}).mappings().all()
    return [
        {
            "id": row["id"],
            "class_number": row["class_number"],
            "word": row["word"],
            "answer": row["answer"],
            "is_active": row["is_active"],
        }
        for row in rows
    ]


def get_russian_vocabulary_map(session: Session, class_number: int | None = None) -> dict[str, str]:
    return {item["word"]: item["answer"] for item in get_russian_vocabulary_words(session, class_number)}


def get_russian_vocabulary_word_list(session: Session, class_number: int | None = None) -> list[str]:
    return [item["word"] for item in get_russian_vocabulary_words(session, class_number)]
