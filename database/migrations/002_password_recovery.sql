-- Migration 002: password recovery and password history.
-- Run this script in DBeaver against arina_db.

CREATE SCHEMA IF NOT EXISTS arina;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS arina.password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES arina.users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    used_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS arina.password_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES arina.users(id) ON DELETE CASCADE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id
    ON arina.password_reset_tokens(user_id);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token
    ON arina.password_reset_tokens(token);

CREATE INDEX IF NOT EXISTS idx_password_history_user_id_created_at
    ON arina.password_history(user_id, created_at DESC);
