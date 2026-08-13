from decimal import Decimal, ROUND_HALF_UP

from Arina.auth.services import decode_jwt_token, get_token_user_id
from Arina.database.session import get_session_factory
from Arina.typing_trainer.levels import ANIMALS, LAYOUT_TITLES, get_level, get_layout_levels, get_max_level
from Arina.typing_trainer.repositories import TypingTrainerRepository


class TypingTrainerValidationError(Exception):
    """Validation error for touch typing trainer payloads."""


def get_user_id_from_access_token(access_token: str) -> int:
    """Decode access token and return authenticated user id."""
    payload = decode_jwt_token(access_token, expected_type="access")
    return get_token_user_id(payload)


def to_decimal(value: int | float | str) -> Decimal:
    """Normalize numeric value to Decimal with two fractional digits."""
    return Decimal(str(value or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_layout(layout_code: str) -> str:
    """Validate and normalize keyboard layout code."""
    layout = str(layout_code or "ru").strip().lower()
    if layout not in LAYOUT_TITLES:
        raise TypingTrainerValidationError("Неизвестная раскладка клавиатуры.")
    return layout


def validate_animal(animal_code: str) -> str:
    """Validate and normalize animal character code."""
    animal = str(animal_code or "dino").strip().lower()
    if animal not in ANIMALS:
        raise TypingTrainerValidationError("Неизвестный персонаж.")
    return animal


def progress_to_dict(progress) -> dict:
    """Convert progress SQLAlchemy model to API dict."""
    return {
        "layout_code": progress.layout_code,
        "animal_code": progress.animal_code,
        "current_level": progress.current_level,
        "max_unlocked_level": progress.max_unlocked_level,
        "total_attempts": progress.total_attempts,
        "best_accuracy": float(progress.best_accuracy or 0),
        "best_speed_cpm": float(progress.best_speed_cpm or 0),
    }


def attempt_to_dict(attempt) -> dict:
    """Convert attempt SQLAlchemy model to API dict."""
    return {
        "id": attempt.id,
        "layout_code": attempt.layout_code,
        "level_number": attempt.level_number,
        "animal_code": attempt.animal_code,
        "animal": ANIMALS.get(attempt.animal_code, ANIMALS["dino"]),
        "total_letters": attempt.total_letters,
        "correct_letters": attempt.correct_letters,
        "wrong_letters": attempt.wrong_letters,
        "missed_letters": attempt.missed_letters,
        "early_hits": attempt.early_hits,
        "late_hits": attempt.late_hits,
        "accuracy_percent": float(attempt.accuracy_percent or 0),
        "duration_seconds": float(attempt.duration_seconds or 0),
        "speed_cpm": float(attempt.speed_cpm or 0),
        "is_passed": bool(attempt.is_passed),
        "created_at": attempt.created_at.isoformat() if attempt.created_at else None,
    }


def level_to_dict(level: dict, progress, best_attempt) -> dict:
    """Build UI state for one level using user progress."""
    level_number = int(level["level"])
    is_locked = level_number > int(progress.max_unlocked_level or 1)
    is_completed = bool(best_attempt and best_attempt.is_passed)
    return {
        **level,
        "is_locked": is_locked,
        "is_current": level_number == int(progress.current_level or 1),
        "is_completed": is_completed,
        "status_title": "Закрыт" if is_locked else "Пройден" if is_completed else "Открыт",
        "best_attempt": attempt_to_dict(best_attempt) if best_attempt else None,
    }


def get_progress(access_token: str, layout_code: str) -> dict:
    """Return current progress for selected keyboard layout."""
    user_id = get_user_id_from_access_token(access_token)
    layout = validate_layout(layout_code)
    session_factory = get_session_factory()
    with session_factory() as session:
        repository = TypingTrainerRepository(session)
        progress = repository.get_or_create_progress(user_id, layout)
        session.commit()
        return {"status": "ok", "progress": progress_to_dict(progress)}


def get_levels_summary(access_token: str, layout_code: str) -> dict:
    """Return layout progress, levels, and recent attempts for the levels page."""
    user_id = get_user_id_from_access_token(access_token)
    layout = validate_layout(layout_code)
    session_factory = get_session_factory()
    with session_factory() as session:
        repository = TypingTrainerRepository(session)
        progress = repository.get_or_create_progress(user_id, layout)
        best_by_level = repository.get_best_attempts_by_level(user_id, layout)
        recent_attempts = repository.get_recent_attempts(user_id, layout, limit=8)
        levels = [level_to_dict(level, progress, best_by_level.get(level["level"])) for level in get_layout_levels(layout)]
        session.commit()
        return {
            "status": "ok",
            "layout_code": layout,
            "layout_title": LAYOUT_TITLES[layout],
            "progress": progress_to_dict(progress),
            "levels": levels,
            "recent_attempts": [attempt_to_dict(attempt) for attempt in recent_attempts],
        }


def save_animal(access_token: str, layout_code: str, animal_code: str) -> dict:
    """Save selected animal for the authenticated user."""
    user_id = get_user_id_from_access_token(access_token)
    layout = validate_layout(layout_code)
    animal = validate_animal(animal_code)
    session_factory = get_session_factory()
    with session_factory() as session:
        repository = TypingTrainerRepository(session)
        progress = repository.update_animal(user_id, layout, animal)
        session.commit()
        return {"status": "ok", "progress": progress_to_dict(progress)}


def save_attempt(access_token: str, payload: dict) -> dict:
    """Validate and save one level attempt."""
    if not isinstance(payload, dict):
        raise TypingTrainerValidationError("Не переданы результаты уровня.")
    user_id = get_user_id_from_access_token(access_token)
    layout = validate_layout(payload.get("layout_code"))
    animal = validate_animal(payload.get("animal_code"))
    level_number = int(payload.get("level_number") or 1)
    level = get_level(layout, level_number)
    required_accuracy = Decimal(str(level.get("required_accuracy", 80)))
    total_letters = int(payload.get("total_letters") or 0)
    correct_letters = int(payload.get("correct_letters") or 0)
    wrong_letters = int(payload.get("wrong_letters") or 0)
    missed_letters = int(payload.get("missed_letters") or 0)
    early_hits = int(payload.get("early_hits") or 0)
    late_hits = int(payload.get("late_hits") or 0)
    duration_seconds = to_decimal(payload.get("duration_seconds") or 0)
    accuracy_percent = to_decimal(payload.get("accuracy_percent") or 0)
    speed_cpm = to_decimal(payload.get("speed_cpm") or 0)
    is_passed = bool(payload.get("is_passed")) and accuracy_percent >= required_accuracy
    session_factory = get_session_factory()
    with session_factory() as session:
        repository = TypingTrainerRepository(session)
        progress = repository.get_or_create_progress(user_id, layout, animal)
        attempt = repository.create_attempt(user_id, layout, level_number, animal, total_letters, correct_letters, wrong_letters, missed_letters, early_hits, late_hits, accuracy_percent, duration_seconds, speed_cpm, is_passed)
        repository.apply_attempt_to_progress(progress, level_number, accuracy_percent, speed_cpm, is_passed, get_max_level(layout))
        session.commit()
        return {
            "status": "ok",
            "is_passed": is_passed,
            "required_accuracy": float(required_accuracy),
            "attempt": attempt_to_dict(attempt),
            "progress": progress_to_dict(progress),
        }
