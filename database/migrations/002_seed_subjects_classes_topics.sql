-- Migration 002: seed reference data for subjects, school classes and class 1 topics.
-- Safe to re-run: all inserts use ON CONFLICT.

INSERT INTO arina.subjects (code, title, is_active)
VALUES
    ('math', 'Математика', TRUE),
    ('russian', 'Русский язык', TRUE),
    ('world', 'Окружающий мир', TRUE),
    ('english', 'Английский язык', TRUE)
ON CONFLICT (code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;

INSERT INTO arina.school_classes (class_number, title)
VALUES
    (1, '1 класс'),
    (2, '2 класс'),
    (3, '3 класс'),
    (4, '4 класс'),
    (5, '5 класс'),
    (6, '6 класс'),
    (7, '7 класс'),
    (8, '8 класс'),
    (9, '9 класс'),
    (10, '10 класс'),
    (11, '11 класс')
ON CONFLICT (class_number) DO UPDATE
SET title = EXCLUDED.title;

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'math')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, seed.class_number, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    (1, 'counting', 'Счёт предметов'),
    (1, 'number_line', 'Числовой отрезок'),
    (1, 'compare_numbers', 'Сравнение чисел'),
    (1, 'number_composition', 'Состав числа'),
    (1, 'addition_to_10', 'Сложение в пределах 10'),
    (1, 'subtraction_to_10', 'Вычитание в пределах 10'),
    (1, 'add_sub_to_20', 'Сложение и вычитание в пределах 20'),
    (1, 'missing_number', 'Неизвестное число'),
    (1, 'word_problems', 'Задачи'),
    (1, 'geometry', 'Геометрические фигуры'),
    (1, 'measurements', 'Величины и измерения')
) AS seed(class_number, code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'russian')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, seed.class_number, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    (1, 'sounds_and_letters', 'Звуки и буквы'),
    (1, 'vowels', 'Гласные звуки и буквы'),
    (1, 'consonants', 'Согласные звуки и буквы'),
    (1, 'hard_soft_consonants', 'Твёрдые и мягкие согласные'),
    (1, 'voiced_voiceless', 'Звонкие и глухие согласные'),
    (1, 'syllable', 'Слог'),
    (1, 'stress', 'Ударение'),
    (1, 'word', 'Слово'),
    (1, 'sentence', 'Предложение'),
    (1, 'capital_letter', 'Заглавная буква'),
    (1, 'punctuation', 'Знаки препинания'),
    (1, 'word_transfer', 'Перенос слов'),
    (1, 'zhi_shi_cha_shcha_chu_shchu', 'ЖИ-ШИ, ЧА-ЩА, ЧУ-ЩУ'),
    (1, 'mini_dictations', 'Мини-диктанты')
) AS seed(class_number, code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'world')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, seed.class_number, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    (1, 'living_nonliving', 'Живая и неживая природа'),
    (1, 'plants', 'Растения'),
    (1, 'animals', 'Животные'),
    (1, 'seasons', 'Времена года'),
    (1, 'time', 'Время'),
    (1, 'family_school', 'Семья и школа'),
    (1, 'safety', 'Безопасность'),
    (1, 'health', 'Здоровье'),
    (1, 'senses', 'Органы чувств'),
    (1, 'professions', 'Профессии')
) AS seed(class_number, code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;
