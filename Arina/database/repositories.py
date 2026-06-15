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

    def get_subjects(self) -> list[dict]:
        rows = self.session.scalars(
            select(Subject)
            .where(Subject.is_active.is_(True))
            .order_by(Subject.id)
        ).all()
        return [
            {
                "id": row.id,
                "code": row.code,
                "title": row.title,
                "is_active": row.is_active,
            }
            for row in rows
        ]

    def get_school_classes(self) -> list[dict]:
        rows = self.session.scalars(
            select(SchoolClass).order_by(SchoolClass.class_number)
        ).all()
        return [
            {
                "id": row.id,
                "class_number": row.class_number,
                "title": row.title,
            }
            for row in rows
        ]

    def get_topics(self, subject_code: str | None = None, class_number: int | None = None) -> list[dict]:
        query = (
            select(Topic, Subject.code.label("subject_code"), Subject.title.label("subject_title"))
            .join(Subject, Topic.subject_id == Subject.id)
            .where(Topic.is_active.is_(True))
            .order_by(Subject.id, Topic.class_number, Topic.id)
        )

        if subject_code:
            query = query.where(Subject.code == subject_code)
        if class_number:
            query = query.where(Topic.class_number == class_number)

        rows = self.session.execute(query).all()
        return [
            {
                "id": topic.id,
                "subject_id": topic.subject_id,
                "subject_code": row.subject_code,
                "subject_title": row.subject_title,
                "class_number": topic.class_number,
                "code": topic.code,
                "title": topic.title,
                "is_active": topic.is_active,
            }
            for row in rows
            for topic in [row[0]]
        ]

    def get_summary(self) -> dict:
        return {
            "subjects": self.count_subjects(),
            "school_classes": self.count_school_classes(),
            "topics": self.count_topics(),
        }
