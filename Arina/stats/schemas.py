from dataclasses import dataclass
from decimal import Decimal
from typing import Any


class StatsValidationError(ValueError):
    """Raised when the stats API payload is invalid."""


@dataclass(frozen=True)
class TestAttemptPayload:
    subject_code: str
    class_number: int
    topic_code: str | None
    total_questions: int
    correct_answers: int
    wrong_answers: int
    empty_answers: int
    score_percent: Decimal
    time_spent_seconds: int
    average_time_seconds: Decimal
    answers: list[dict[str, Any]]


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


def parse_test_attempt_payload(payload: Any) -> TestAttemptPayload:
    if not isinstance(payload, dict):
        raise StatsValidationError("JSON body is required")

    subject_code = str(payload.get("subject_code") or payload.get("subject") or "").strip()
    if not subject_code:
        raise StatsValidationError("Предмет не найден.")

    answers = payload.get("answers") if isinstance(payload.get("answers"), list) else []

    return TestAttemptPayload(
        subject_code=subject_code,
        class_number=to_int(payload.get("class_number"), 1),
        topic_code=str(payload.get("topic_code") or "").strip() or None,
        total_questions=max(0, to_int(payload.get("total_questions"), 0)),
        correct_answers=max(0, to_int(payload.get("correct_answers"), 0)),
        wrong_answers=max(0, to_int(payload.get("wrong_answers"), 0)),
        empty_answers=max(0, to_int(payload.get("empty_answers"), 0)),
        score_percent=to_decimal(payload.get("score_percent"), Decimal("0")),
        time_spent_seconds=max(0, to_int(payload.get("time_spent_seconds"), 0)),
        average_time_seconds=to_decimal(payload.get("average_time_seconds"), Decimal("0")),
        answers=answers,
    )
