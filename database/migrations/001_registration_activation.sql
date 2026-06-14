-- Migration 001: registration and email activation support.
-- Run this script in DBeaver against arina_db.

CREATE SCHEMA IF NOT EXISTS arina;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

ALTER TABLE arina.users
    ALTER COLUMN is_active SET DEFAULT FALSE;

ALTER TABLE arina.students
    ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);

CREATE TABLE IF NOT EXISTS arina.account_activation_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES arina.users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    used_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_account_activation_tokens_user_id
    ON arina.account_activation_tokens(user_id);

CREATE INDEX IF NOT EXISTS idx_account_activation_tokens_token
    ON arina.account_activation_tokens(token);
