from sqlalchemy import text
from sqlalchemy.orm import Session


ENGLISH_VOCABULARY_SELECT = text(
    """
    SELECT id, class_number, english_word, russian_translation, transcription, is_active
    FROM arina.english_vocabulary_words
    WHERE is_active = true
      AND (:class_number IS NULL OR class_number = :class_number)
    ORDER BY class_number, english_word
    """
)


def get_english_vocabulary_words(session: Session, class_number: int | None = None) -> list[dict]:
    rows = session.execute(ENGLISH_VOCABULARY_SELECT, {"class_number": class_number}).mappings().all()
    return [
        {
            "id": row["id"],
            "class_number": row["class_number"],
            "en": [row["english_word"]],
            "ru": [row["russian_translation"]],
            "transcription": [row["transcription"] or ""],
            "is_active": row["is_active"],
        }
        for row in rows
    ]
