-- Migration 003: rebuild auth/user result tables with integer IDs.
-- IMPORTANT: this migration is intended for the current development stage.
-- It drops existing user accounts, students, attempts, answers and auth tokens.
-- Run it in DBeaver against arina_db only after you confirm that test data may be recreated.

CREATE SCHEMA IF NOT EXISTS arina;

DROP TABLE IF EXISTS arina.password_history CASCADE;
DROP TABLE IF EXISTS arina.password_reset_tokens CASCADE;
DROP TABLE IF EXISTS arina.account_activation_tokens CASCADE;
DROP TABLE IF EXISTS arina.test_answers CASCADE;
DROP TABLE IF EXISTS arina.test_attempts CASCADE;
DROP TABLE IF EXISTS arina.students CASCADE;
DROP TABLE IF EXISTS arina.users CASCADE;

CREATE TABLE arina.users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE arina.students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES arina.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    class_number INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE arina.test_attempts (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES arina.students(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES arina.subjects(id),
    class_number INTEGER NOT NULL,
    topic_id INTEGER REFERENCES arina.topics(id),
    total_questions INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL DEFAULT 0,
    wrong_answers INTEGER NOT NULL DEFAULT 0,
    empty_answers INTEGER NOT NULL DEFAULT 0,
    score_percent NUMERIC(5,2) NOT NULL DEFAULT 0,
    grade INTEGER,
    time_spent_seconds INTEGER DEFAULT 0,
    average_time_seconds NUMERIC(7,2),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE arina.test_answers (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER NOT NULL REFERENCES arina.test_attempts(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    user_answer TEXT,
    correct_answer TEXT,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    answer_type VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE arina.account_activation_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES arina.users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    used_at TIMESTAMP
);

CREATE TABLE arina.password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES arina.users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    used_at TIMESTAMP
);

CREATE TABLE arina.password_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES arina.users(id) ON DELETE CASCADE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_students_user_id ON arina.students(user_id);
CREATE INDEX idx_test_attempts_student_id ON arina.test_attempts(student_id);
CREATE INDEX idx_test_answers_attempt_id ON arina.test_answers(attempt_id);
CREATE INDEX idx_account_activation_tokens_user_id ON arina.account_activation_tokens(user_id);
CREATE INDEX idx_account_activation_tokens_token ON arina.account_activation_tokens(token);
CREATE INDEX idx_password_reset_tokens_user_id ON arina.password_reset_tokens(user_id);
CREATE INDEX idx_password_reset_tokens_token ON arina.password_reset_tokens(token);
CREATE INDEX idx_password_history_user_id_created_at ON arina.password_history(user_id, created_at DESC);
