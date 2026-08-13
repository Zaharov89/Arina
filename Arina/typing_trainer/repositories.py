from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from Arina.database.models import TypingTrainerAttempt, TypingTrainerProgress


class TypingTrainerRepository:
    """Database operations for touch typing progress and attempts."""

    def __init__(self, session: Session):
        self.session = session

    def get_progress(self, user_id: int, layout_code: str) -> TypingTrainerProgress | None:
        return self.session.scalar(
            select(TypingTrainerProgress).where(
                TypingTrainerProgress.user_id == user_id,
                TypingTrainerProgress.layout_code == layout_code,
            )
        )

    def get_or_create_progress(self, user_id: int, layout_code: str, animal_code: str = "dino") -> TypingTrainerProgress:
        progress = self.get_progress(user_id, layout_code)
        if progress:
            return progress
        progress = TypingTrainerProgress(user_id=user_id, layout_code=layout_code, animal_code=animal_code)
        self.session.add(progress)
        self.session.flush()
        return progress

    def update_animal(self, user_id: int, layout_code: str, animal_code: str) -> TypingTrainerProgress:
        progress = self.get_or_create_progress(user_id, layout_code, animal_code)
        progress.animal_code = animal_code
        self.session.flush()
        return progress

    def create_attempt(
        self,
        user_id: int,
        layout_code: str,
        level_number: int,
        animal_code: str,
        total_letters: int,
        correct_letters: int,
        wrong_letters: int,
        missed_letters: int,
        early_hits: int,
        late_hits: int,
        accuracy_percent: Decimal,
        duration_seconds: Decimal,
        speed_cpm: Decimal,
        is_passed: bool,
    ) -> TypingTrainerAttempt:
        attempt = TypingTrainerAttempt(
            user_id=user_id,
            layout_code=layout_code,
            level_number=level_number,
            animal_code=animal_code,
            total_letters=total_letters,
            correct_letters=correct_letters,
            wrong_letters=wrong_letters,
            missed_letters=missed_letters,
            early_hits=early_hits,
            late_hits=late_hits,
            accuracy_percent=accuracy_percent,
            duration_seconds=duration_seconds,
            speed_cpm=speed_cpm,
            is_passed=is_passed,
        )
        self.session.add(attempt)
        self.session.flush()
        return attempt

    @staticmethod
    def apply_attempt_to_progress(progress: TypingTrainerProgress, level_number: int, accuracy_percent: Decimal, speed_cpm: Decimal, is_passed: bool, max_level: int) -> None:
        progress.total_attempts += 1
        if accuracy_percent > progress.best_accuracy:
            progress.best_accuracy = accuracy_percent
        if speed_cpm > progress.best_speed_cpm:
            progress.best_speed_cpm = speed_cpm
        if is_passed and level_number >= progress.max_unlocked_level:
            progress.max_unlocked_level = min(level_number + 1, max_level)
            progress.current_level = progress.max_unlocked_level
