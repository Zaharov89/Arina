-- Migration 011: disable deprecated class 3 math topics.
-- Fractions are not used in class 3, and multiplication/division should stay only within multiplication table tasks.
-- Safe to re-run.

WITH subject_row AS (
    SELECT id FROM arina.subjects WHERE code = 'math'
)
UPDATE arina.topics topic
SET is_active = FALSE
FROM subject_row
WHERE topic.subject_id = subject_row.id
  AND topic.class_number = 3
  AND topic.code IN ('fractions_intro', 'multiply_divide_by_10_100');
