-- Migration 008: merge similar world topics for class 2 and 3.
-- Safe to re-run.

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'world')
INSERT INTO arina.topics (subject_id, class_number, code, title, is_active)
SELECT subject_row.id, seed.class_number, seed.code, seed.title, TRUE
FROM subject_row
CROSS JOIN (VALUES
    (2, 'nature_weather_2', 'Природа и погода'),
    (2, 'human_health_2', 'Здоровье человека и органы чувств'),
    (2, 'hometown_russia_2', 'Родной край и Россия'),
    (3, 'our_planet_3', 'Наша планета')
) AS seed(class_number, code, title)
ON CONFLICT (subject_id, class_number, code) DO UPDATE
SET title = EXCLUDED.title,
    is_active = TRUE;

WITH subject_row AS (SELECT id FROM arina.subjects WHERE code = 'world')
UPDATE arina.topics t
SET is_active = FALSE
FROM subject_row
WHERE t.subject_id = subject_row.id
  AND (
      (t.class_number = 2 AND t.code IN ('nature_living_nonliving_2', 'natural_phenomena', 'seasons_weather_2', 'senses_2', 'hometown', 'russia_symbols'))
      OR
      (t.class_number = 3 AND t.code IN ('earth_planet', 'continents_oceans', 'map_globe', 'water_cycle', 'air_water_soil'))
  );
