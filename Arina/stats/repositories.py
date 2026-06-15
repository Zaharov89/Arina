from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from Arina.database.models import Student, Subject, TestAnswer, TestAttempt, Topic, User


class StatsRepository:
    """Database operations for diary stats and test attempts."""

    def __init__(self, session: Session):
        self.session = session

    def get_user(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_student_by_user_id(self, user_id: int) -> Student | None:
        return self.session.scalar(select(Student).where(Student.user_id == user_id).order_by(Student.id).limit(1))

    def get_subject(self, subject_code: str) -> Subject | None:
        return self.session.scalar(select(Subject).where(Subject.code == subject_code))

    def get_topic(self, subject: Subject, class_number: int, topic_code: str | None) -> Topic | None:
        if not topic_code:
            return None
        return self.session.scalar(
            select(Topic).where(
                Topic.subject_id == subject.id,
                Topic.class_number == class_number,
                Topic.code == topic_code,
            )
        )

    def get_subject_topics(self, subject: Subject) -> list[Topic]:
        return list(
            self.session.scalars(
                select(Topic)
                .where(Topic.subject_id == subject.id, Topic.is_active.is_(True))
                .order_by(Topic.class_number, Topic.id)
            ).all()
        )

    def get_grade_rows(self, student: Student, subject: Subject, start_date: date):
        return self.session.execute(
            select(
                cast(TestAttempt.created_at, Date).label("grade_date"),
                TestAttempt.topic_id.label("topic_id"),
                Topic.code.label("topic_code"),
                Topic.title.label("topic_title"),
                func.max(TestAttempt.grade).label("grade"),
            )
            .select_from(TestAttempt)
            .outerjoin(Topic, TestAttempt.topic_id == Topic.id)
            .where(
                TestAttempt.student_id == student.id,
                TestAttempt.subject_id == subject.id,
                TestAttempt.grade.is_not(None),
                cast(TestAttempt.created_at, Date) >= start_date,
            )
            .group_by(cast(TestAttempt.created_at, Date), TestAttempt.topic_id, Topic.code, Topic.title)
            .order_by(cast(TestAttempt.created_at, Date).desc(), Topic.title)
        ).all()

    def find_today_attempt(self, student_id: int, subject_id: int, topic_id: int | None) -> TestAttempt | None:
        today = date.today()
        query = select(TestAttempt).where(
            TestAttempt.student_id == student_id,
            TestAttempt.subject_id == subject_id,
            cast(TestAttempt.created_at, Date) == today,
        )
        if topic_id is None:
            query = query.where(TestAttempt.topic_id.is_(None))
        else:
            query = query.where(TestAttempt.topic_id == topic_id)

        return self.session.scalar(query.order_by(TestAttempt.created_at.desc()).limit(1))

    def create_attempt(
        self,
        student_id: int,
        subject_id: int,
        class_number: int,
        topic_id: int | None,
        total_questions: int,
        correct_answers: int,
        wrong_answers: int,
        empty_answers: int,
        score_percent: Decimal,
        grade: int,
        time_spent_seconds: int,
        average_time_seconds: Decimal,
    ) -> TestAttempt:
        attempt = TestAttempt(
            student_id=student_id,
            subject_id=subject_id,
            class_number=class_number,
            topic_id=topic_id,
            total_questions=total_questions,
            correct_answers=correct_answers,
            wrong_answers=wrong_answers,
            empty_answers=empty_answers,
            score_percent=score_percent,
            grade=grade,
            time_spent_seconds=time_spent_seconds,
            average_time_seconds=average_time_seconds,
        )
        self.session.add(attempt)
        self.session.flush()
        return attempt

    @staticmethod
    def update_attempt(
        attempt: TestAttempt,
        class_number: int,
        total_questions: int,
        correct_answers: int,
        wrong_answers: int,
        empty_answers: int,
        score_percent: Decimal,
        grade: int,
        time_spent_seconds: int,
        average_time_seconds: Decimal,
    ) -> None:
        attempt.class_number = class_number
        attempt.total_questions = total_questions
        attempt.correct_answers = correct_answers
        attempt.wrong_answers = wrong_answers
        attempt.empty_answers = empty_answers
        attempt.score_percent = score_percent
        attempt.grade = grade
        attempt.time_spent_seconds = time_spent_seconds
        attempt.average_time_seconds = average_time_seconds

    def replace_attempt_answers(self, attempt: TestAttempt, answers: list[dict[str, Any]]) -> None:
        self.session.query(TestAnswer).filter(TestAnswer.attempt_id == attempt.id).delete(synchronize_session=False)
        for answer in answers:
            question_text = str(answer.get("question") or answer.get("question_text") or answer.get("example") or "Задание")
            self.session.add(
                TestAnswer(
                    attempt_id=attempt.id,
                    question_text=question_text,
                    user_answer=None if answer.get("userAnswer") is None else str(answer.get("userAnswer")),
                    correct_answer=None if answer.get("correctAnswer") is None else str(answer.get("correctAnswer")),
                    is_correct=bool(answer.get("is_correct", False)),
                    answer_type=answer.get("answer_type"),
                )
            )
