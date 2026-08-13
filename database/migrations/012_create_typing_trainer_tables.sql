-- Migration 012: create tables for the additional keyboard touch typing trainer.
-- Safe to re-run.

CREATE SCHEMA IF NOT EXISTS arina;

CREATE TABLE IF NOT EXISTS arina.typing_trainer_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES arina.users(id) ON DELETE CASCADE,
    layout_code VARCHAR(10) NOT NULL,
    animal_code VARCHAR(30) NOT NULL DEFAULT 'dino',
    current_level INTEGER NOT NULL DEFAULT 1,
    max_unlocked_level INTEGER NOT NULL DEFAULT 1,
    total_attempts INTEGER NOT NULL DEFAULT 0,
    best_accuracy NUMERIC(5, 2) NOT NULL DEFAULT 0,
    best_speed_cpm NUMERIC(7, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT typing_trainer_progress_user_layout_key UNIQUE (user_id, layout_code),
    CONSTRAINT typing_trainer_progress_layout_check CHECK (layout_code IN ('ru', 'en')),
    CONSTRAINT typing_trainer_progress_animal_check CHECK (animal_code IN ('dino', 'cat', 'dog'))
);

CREATE TABLE IF NOT EXISTS arina.typing_trainer_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES arina.users(id) ON DELETE CASCADE,
    layout_code VARCHAR(10) NOT NULL,
    level_number INTEGER NOT NULL,
    animal_code VARCHAR(30) NOT NULL DEFAULT 'dino',
    total_letters INTEGER NOT NULL DEFAULT 0,
    correct_letters INTEGER NOT NULL DEFAULT 0,
    wrong_letters INTEGER NOT NULL DEFAULT 0,
    missed_letters INTEGER NOT NULL DEFAULT 0,
    early_hits INTEGER NOT NULL DEFAULT 0,
    late_hits INTEGER NOT NULL DEFAULT 0,
    accuracy_percent NUMERIC(5, 2) NOT NULL DEFAULT 0,
    duration_seconds NUMERIC(8, 2) NOT NULL DEFAULT 0,
    speed_cpm NUMERIC(7, 2) NOT NULL DEFAULT 0,
    is_passed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT typing_trainer_attempts_layout_check CHECK (layout_code IN ('ru', 'en')),
    CONSTRAINT typing_trainer_attempts_animal_check CHECK (animal_code IN ('dino', 'cat', 'dog'))
);

CREATE INDEX IF NOT EXISTS idx_typing_trainer_progress_user_id
    ON arina.typing_trainer_progress(user_id);

CREATE INDEX IF NOT EXISTS idx_typing_trainer_attempts_user_layout_level
    ON arina.typing_trainer_attempts(user_id, layout_code, level_number);
