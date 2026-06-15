-- Migration 007: seed class 3 topics for existing subjects.
-- Safe to re-run.

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'math')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, 3, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    ('numbers_to_1000', 'Числа от 1 до 1000'),
    ('compare_to_1000', 'Сравнение чисел до 1000'),
    ('add_sub_to_1000', 'Сложение и вычитание до 1000'),
    ('multiplication_division_table', 'Табличное умножение и деление'),
    ('multiply_divide_by_10_100', 'Умножение и деление на 10 и 100'),
    ('division_with_remainder', 'Деление с остатком'),
    ('order_of_operations_3', 'Порядок действий'),
    ('equations_3', 'Простые уравнения'),
    ('word_problems_3', 'Задачи в 2–3 действия'),
    ('measurements_3', 'Величины: длина, масса, время'),
    ('area_perimeter', 'Площадь и периметр'),
    ('fractions_intro', 'Доли и простые дроби')
) AS seed(code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'russian')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, 3, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    ('word_structure', 'Состав слова'),
    ('root_prefix_suffix', 'Корень, приставка и суффикс'),
    ('spelling_prefixes', 'Правописание приставок'),
    ('checked_vowels_3', 'Проверяемые безударные гласные'),
    ('paired_consonants_3', 'Парные согласные в корне'),
    ('parts_of_speech_3', 'Части речи. Повторение'),
    ('noun_gender_number_case', 'Имя существительное: род, число, падеж'),
    ('adjective_gender_number', 'Имя прилагательное: род и число'),
    ('verb_tense', 'Глагол: время'),
    ('pronoun_intro', 'Местоимение'),
    ('sentence_homogeneous', 'Предложение и однородные члены'),
    ('text_plan_3', 'Текст, тема и план'),
    ('vocabulary_words_3', 'Словарные слова 3 класса')
) AS seed(code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'world')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, 3, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    ('earth_planet', 'Земля — планета'),
    ('continents_oceans', 'Материки и океаны'),
    ('map_globe', 'Карта и глобус'),
    ('water_cycle', 'Круговорот воды'),
    ('air_water_soil', 'Воздух, вода и почва'),
    ('plants_groups_3', 'Группы растений'),
    ('animals_groups_3', 'Группы животных'),
    ('ecosystems_3', 'Природные сообщества'),
    ('human_body_3', 'Организм человека'),
    ('healthy_lifestyle_3', 'Здоровый образ жизни'),
    ('russia_regions_3', 'Россия: регионы и народы'),
    ('history_intro_3', 'Страницы истории'),
    ('ecology_rules_3', 'Охрана природы')
) AS seed(code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'english')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, 3, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    ('reading_rules_3', 'Правила чтения'),
    ('personal_info_3', 'О себе'),
    ('family_friends_3', 'Семья и друзья'),
    ('numbers_1_100_en', 'Числа 1–100'),
    ('days_months_en', 'Дни недели и месяцы'),
    ('school_subjects_en', 'Школьные предметы'),
    ('daily_routine_en', 'Распорядок дня'),
    ('food_likes_en', 'Еда и предпочтения'),
    ('animals_3_en', 'Животные'),
    ('home_city_en', 'Дом и город'),
    ('present_simple_intro', 'Present Simple'),
    ('questions_short_answers', 'Вопросы и краткие ответы'),
    ('vocabulary_words_en_3', 'Английские слова 3 класса')
) AS seed(code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = EXCLUDED.is_active;
