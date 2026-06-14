import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from Arina.database.config import DATABASE_SCHEMA


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    students: Mapped[list["Student"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    activation_tokens: Mapped[list["AccountActivationToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"
    __table_args__ = {"schema": DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{DATABASE_SCHEMA}.users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(100))
    class_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    user: Mapped[User] = relationship(back_populates="students")
    test_attempts: Mapped[list["TestAttempt"]] = relationship(back_populates="student", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = {"schema": DATABASE_SCHEMA}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    topics: Mapped[list["Topic"]] = relationship(back_populates="subject")
    test_attempts: Mapped[list["TestAttempt"]] = relationship(back_populates="subject")


class SchoolClass(Base):
    __tablename__ = "school_classes"
    __table_args__ = {"schema": DATABASE_SCHEMA}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    class_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(50), nullable=False)


class Topic(Base):
    __tablename__ = "topics"
    __table_args__ = (
        UniqueConstraint("subject_id", "class_number", "code", name="topics_subject_id_class_number_code_key"),
        {"schema": DATABASE_SCHEMA},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{DATABASE_SCHEMA}.subjects.id", ondelete="CASCADE"), nullable=False)
    class_number: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    subject: Mapped[Subject] = relationship(back_populates="topics")
    test_attempts: Mapped[list["TestAttempt"]] = relationship(back_populates="topic")


class TestAttempt(Base):
    __tablename__ = "test_attempts"
    __table_args__ = {"schema": DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{DATABASE_SCHEMA}.students.id", ondelete="CASCADE"), nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer, ForeignKey(f"{DATABASE_SCHEMA}.subjects.id"), nullable=False)
    class_number: Mapped[int] = mapped_column(Integer, nullable=False)
    topic_id: Mapped[int | None] = mapped_column(Integer, ForeignKey(f"{DATABASE_SCHEMA}.topics.id"))
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wrong_answers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    empty_answers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    score_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    grade: Mapped[int | None] = mapped_column(Integer)
    time_spent_seconds: Mapped[int | None] = mapped_column(Integer, default=0)
    average_time_seconds: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    student: Mapped[Student] = relationship(back_populates="test_attempts")
    subject: Mapped[Subject] = relationship(back_populates="test_attempts")
    topic: Mapped[Topic | None] = relationship(back_populates="test_attempts")
    answers: Mapped[list["TestAnswer"]] = relationship(back_populates="attempt", cascade="all, delete-orphan")


class TestAnswer(Base):
    __tablename__ = "test_answers"
    __table_args__ = {"schema": DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{DATABASE_SCHEMA}.test_attempts.id", ondelete="CASCADE"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    user_answer: Mapped[str | None] = mapped_column(Text)
    correct_answer: Mapped[str | None] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    answer_type: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    attempt: Mapped[TestAttempt] = relationship(back_populates="answers")


class AccountActivationToken(Base):
    __tablename__ = "account_activation_tokens"
    __table_args__ = {"schema": DATABASE_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(f"{DATABASE_SCHEMA}.users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    used_at: Mapped[datetime | None] = mapped_column(DateTime)

    user: Mapped[User] = relationship(back_populates="activation_tokens")
