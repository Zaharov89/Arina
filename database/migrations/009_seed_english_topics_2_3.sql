-- Migration 009: seed English topics for 2 and 3 classes so diary can show grades by class/topic.
-- Safe to re-run.

CREATE SCHEMA IF NOT EXISTS arina;

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'english')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, seed.class_number, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    (2, 'alphabet_en', 'English alphabet'),
    (2, 'sounds_reading', 'Первые правила чтения'),
    (2, 'greetings', 'Приветствие и знакомство'),
    (2, 'family_en', 'Family — семья'),
    (2, 'colors_en', 'Colours — цвета'),
    (2, 'numbers_1_10_en', 'Numbers 1–10'),
    (2, 'school_items_en', 'School things — школьные принадлежности'),
    (2, 'toys_en', 'Toys — игрушки'),
    (2, 'animals_en', 'Animals — животные'),
    (2, 'food_en', 'Food — еда'),
    (2, 'home_rooms_en', 'Home — дом и комнаты'),
    (2, 'simple_phrases_en', 'I am / I have / I like'),
    (2, 'vocabulary_words_en_2', 'Слова для заучивания'),
    (3, 'reading_rules_3', 'Правила чтения: sh, ch, ph'),
    (3, 'personal_info_3', 'Рассказ о себе'),
    (3, 'family_friends_3', 'Family and friends'),
    (3, 'numbers_1_100_en', 'Numbers 1–100'),
    (3, 'days_months_en', 'Days and months'),
    (3, 'school_subjects_en', 'School subjects'),
    (3, 'daily_routine_en', 'Daily routine'),
    (3, 'food_likes_en', 'I like / I don''t like'),
    (3, 'animals_3_en', 'Wild animals and pets'),
    (3, 'home_city_en', 'Home and city'),
    (3, 'present_simple_intro', 'Present Simple'),
    (3, 'questions_short_answers', 'Do you...? Yes, I do / No, I don''t'),
    (3, 'vocabulary_words_en_3', 'Слова для заучивания')
) AS seed(class_number, code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = TRUE;
