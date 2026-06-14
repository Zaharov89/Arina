from sqlalchemy import func, select
from sqlalchemy.orm import Session

from Arina.database.models import SchoolClass, Subject, Topic


class ReferenceDataRepository:
    """Read reference data used by the application."""

    def __init__(self, session: Session):
        self.session = session

    def count_subjects(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Subject)) or 0)

    def count_school_classes(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(SchoolClass)) or 0)

    def count_topics(self) -> int:
        return int(self.session.scalar(select(func.count()).select_from(Topic)) or 0)

    def get_summary(self) -> dict:
        return {
            "subjects": self.count_subjects(),
            "school_classes": self.count_school_classes(),
            "topics": self.count_topics(),
        }
