-- Migration 006: seed class 2 topics for existing subjects.
-- Safe to re-run.

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'math')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, 2, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    ('numbers_to_100', 'Числа от 1 до 100'),
    ('compare_to_100', 'Сравнение чисел до 100'),
    ('add_sub_no_crossing', 'Сложение и вычитание без перехода через десяток'),
    ('add_sub_crossing', 'Сложение и вычитание с переходом через десяток'),
    ('addition_table', 'Таблица сложения'),
    ('multiplication_table', 'Таблица умножения'),
    ('division_equal_parts', 'Деление на равные части'),
    ('mul_div_relation', 'Связь умножения и деления'),
    ('word_problems_2', 'Задачи в 1–2 действия'),
    ('measurements_2', 'Величины: длина, масса, время'),
    ('geometry_perimeter', 'Геометрические фигуры и периметр'),
    ('parentheses_2', 'Выражения со скобками')
) AS seed(code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'russian')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, 2, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    ('sounds_letters_review', 'Звуки и буквы. Повторение'),
    ('alphabet', 'Алфавит'),
    ('vowels_consonants', 'Гласные и согласные'),
    ('unstressed_vowels', 'Ударные и безударные гласные'),
    ('checked_unstressed_root', 'Проверяемые безударные гласные в корне'),
    ('paired_consonants', 'Парные звонкие и глухие согласные'),
    ('silent_consonants', 'Непроизносимые согласные'),
    ('separating_soft_sign', 'Разделительный мягкий знак'),
    ('noun', 'Имя существительное'),
    ('adjective', 'Имя прилагательное'),
    ('verb', 'Глагол'),
    ('sentence_members', 'Предложение и главные члены'),
    ('text_theme', 'Текст и тема текста'),
    ('vocabulary_words_2', 'Словарные слова 2 класса')
) AS seed(code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'world')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, 2, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    ('nature_living_nonliving_2', 'Природа живая и неживая'),
    ('natural_phenomena', 'Явления природы'),
    ('seasons_weather_2', 'Сезоны и погода'),
    ('plants_2', 'Растения'),
    ('animals_2', 'Животные'),
    ('human_health_2', 'Человек и здоровье'),
    ('senses_2', 'Органы чувств'),
    ('safety_2', 'Безопасность дома, в школе и на улице'),
    ('family_society', 'Семья и общество'),
    ('hometown', 'Родной город или село'),
    ('russia_symbols', 'Россия и государственные символы'),
    ('professions_2', 'Профессии'),
    ('ecology_2', 'Экология и бережное отношение к природе')
) AS seed(code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'english')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, 2, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    ('alphabet_en', 'Алфавит'),
    ('sounds_reading', 'Звуки и чтение простых слов'),
    ('greetings', 'Приветствие и знакомство'),
    ('family_en', 'Я и моя семья'),
    ('colors_en', 'Цвета'),
    ('numbers_1_10_en', 'Числа 1–10'),
    ('school_items_en', 'Школьные предметы'),
    ('toys_en', 'Игрушки'),
    ('animals_en', 'Животные'),
    ('food_en', 'Еда'),
    ('home_rooms_en', 'Дом и комнаты'),
    ('simple_phrases_en', 'Простые фразы: I am, I have, This is'),
    ('vocabulary_words_en_2', 'Английские слова 2 класса')
) AS seed(code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;
