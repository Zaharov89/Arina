-- Migration 011: disable class 3 math topic with multiplication/division by 10 and 100.
-- Class 3 multiplication/division should stay only within multiplication table tasks.
-- Safe to re-run.

WITH subject_row AS (
    SELECT id FROM arina.subjects WHERE code = 'math'
)
UPDATE arina.topics topic
SET is_active = FALSE
FROM subject_row
WHERE topic.subject_id = subject_row.id
  AND topic.class_number = 3
  AND topic.code = 'multiply_divide_by_10_100';
