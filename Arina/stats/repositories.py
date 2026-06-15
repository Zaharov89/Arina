import logging
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session

from Arina.database.models import Student, Subject, TestAnswer, TestAttempt, Topic, User

logger = logging.getLogger(__name__)


class StatsRepository:
    """Database operations for diary stats and test attempts."""

    def __init__(self, session: Session):
        self.session = session

    def get_user(self, user_id: int) -> User | None:
        logger.debug("DB get user: user_id=%s", user_id)
        return self.session.get(User, user_id)

    def get_student_by_user_id(self, user_id: int) -> Student | None:
        logger.debug("DB get student by user_id=%s", user_id)
        return self.session.scalar(select(Student).where(Student.user_id == user_id).order_by(Student.id).limit(1))

    def get_subject(self, subject_code: str) -> Subject | None:
        logger.debug("DB get subject: code=%s", subject_code)
        return self.session.scalar(select(Subject).where(Subject.code == subject_code))

    def get_topic(self, subject: Subject, class_number: int, topic_code: str | None) -> Topic | None:
        if not topic_code:
            return None
        logger.debug("DB get topic: subject_id=%s class=%s code=%s", subject.id, class_number, topic_code)
        return self.session.scalar(select(Topic).where(Topic.subject_id == subject.id, Topic.class_number == class_number, Topic.code == topic_code))

    def get_or_create_inactive_topic(self, subject: Subject, class_number: int, topic_code: str, title: str) -> Topic:
        topic = self.get_topic(subject, class_number, topic_code)
        if topic:
            return topic
        logger.info("DB create inactive topic: subject_id=%s class=%s code=%s", subject.id, class_number, topic_code)
        topic = Topic(subject_id=subject.id, class_number=class_number, code=topic_code, title=title, is_active=False)
        self.session.add(topic)
        self.session.flush()
        return topic

    def get_subject_topics(self, subject: Subject) -> list[Topic]:
        logger.debug("DB get active subject topics: subject_id=%s", subject.id)
        return list(self.session.scalars(select(Topic).where(Topic.subject_id == subject.id, Topic.is_active.is_(True)).order_by(Topic.class_number, Topic.id)).all())

    def get_grade_rows(self, student: Student, subject: Subject, start_date: date):
        logger.debug("DB get grade rows: student_id=%s subject_id=%s start=%s", student.id, subject.id, start_date)
        return self.session.execute(
            select(
                cast(TestAttempt.created_at, Date).label("grade_date"),
                TestAttempt.class_number.label("class_number"),
                TestAttempt.topic_id.label("topic_id"),
                Topic.code.label("topic_code"),
                Topic.title.label("topic_title"),
                func.max(TestAttempt.grade).label("grade"),
            )
            .select_from(TestAttempt)
            .outerjoin(Topic, TestAttempt.topic_id == Topic.id)
            .where(TestAttempt.student_id == student.id, TestAttempt.subject_id == subject.id, TestAttempt.grade.is_not(None), cast(TestAttempt.created_at, Date) >= start_date)
            .group_by(cast(TestAttempt.created_at, Date), TestAttempt.class_number, TestAttempt.topic_id, Topic.code, Topic.title)
            .order_by(cast(TestAttempt.created_at, Date).desc(), Topic.title)
        ).all()

    def find_today_attempt(self, student_id: int, subject_id: int, topic_id: int | None) -> TestAttempt | None:
        today = date.today()
        logger.debug("DB find today attempt: student_id=%s subject_id=%s topic_id=%s date=%s", student_id, subject_id, topic_id, today)
        query = select(TestAttempt).where(TestAttempt.student_id == student_id, TestAttempt.subject_id == subject_id, cast(TestAttempt.created_at, Date) == today)
        if topic_id is None:
            query = query.where(TestAttempt.topic_id.is_(None))
        else:
            query = query.where(TestAttempt.topic_id == topic_id)
        return self.session.scalar(query.order_by(TestAttempt.created_at.desc()).limit(1))

    def create_attempt(self, student_id: int, subject_id: int, class_number: int, topic_id: int | None, total_questions: int, correct_answers: int, wrong_answers: int, empty_answers: int, score_percent: Decimal, grade: int, time_spent_seconds: int, average_time_seconds: Decimal) -> TestAttempt:
        logger.info("DB create attempt: student_id=%s subject_id=%s class=%s topic_id=%s grade=%s", student_id, subject_id, class_number, topic_id, grade)
        attempt = TestAttempt(student_id=student_id, subject_id=subject_id, class_number=class_number, topic_id=topic_id, total_questions=total_questions, correct_answers=correct_answers, wrong_answers=wrong_answers, empty_answers=empty_answers, score_percent=score_percent, grade=grade, time_spent_seconds=time_spent_seconds, average_time_seconds=average_time_seconds)
        self.session.add(attempt)
        self.session.flush()
        return attempt

    @staticmethod
    def update_attempt(attempt: TestAttempt, class_number: int, total_questions: int, correct_answers: int, wrong_answers: int, empty_answers: int, score_percent: Decimal, grade: int, time_spent_seconds: int, average_time_seconds: Decimal) -> None:
        logger.info("DB update attempt: attempt_id=%s class=%s grade=%s", attempt.id, class_number, grade)
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
        logger.debug("DB replace attempt answers: attempt_id=%s answers=%s", attempt.id, len(answers or []))
        self.session.query(TestAnswer).filter(TestAnswer.attempt_id == attempt.id).delete(synchronize_session=False)
        for answer in answers:
            question_text = str(answer.get("question") or answer.get("question_text") or answer.get("example") or "Задание")
            self.session.add(TestAnswer(attempt_id=attempt.id, question_text=question_text, user_answer=str(answer.get("userAnswer") or answer.get("user_answer") or ""), correct_answer=str(answer.get("correctAnswer") or answer.get("correct_answer") or answer.get("correct") or ""), is_correct=bool(answer.get("is_correct", False))))
