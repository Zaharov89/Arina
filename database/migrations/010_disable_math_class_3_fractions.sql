-- Migration 010: disable fractions in math class 3.
-- Safe to re-run.

WITH subject_row AS (
    SELECT id FROM arina.subjects WHERE code = 'math'
)
UPDATE arina.topics topic
SET is_active = FALSE
FROM subject_row
WHERE topic.subject_id = subject_row.id
  AND topic.class_number = 3
  AND topic.code = 'fractions_intro';
