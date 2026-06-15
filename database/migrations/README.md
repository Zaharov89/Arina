# Миграции PostgreSQL для Arina

Миграции выполняются вручную в DBeaver через `Alt + X` или через `psql` в базе `arina_db`.

Рабочая схема приложения:

```sql
arina
```

## Порядок запуска на чистой БД

Запускать строго по порядку:

```text
001_create_base_schema.sql
002_seed_subjects_classes_topics.sql
004_create_russian_vocabulary_words.sql
005_create_english_vocabulary_words.sql
006_seed_class_2_topics.sql
007_seed_class_3_topics.sql
```

После этого приложение готово к регистрации пользователей, прохождению тестов и сохранению оценок.

## Важное про 003

```text
003_rebuild_auth_tables_with_integer_ids.sql
```

Это dev-only миграция для старого переходного этапа проекта. Она удаляет и пересоздаёт пользовательские таблицы, учеников, результаты тестов и auth-токены.

Не запускай её на рабочей БД с нужными пользователями/оценками.

На новой чистой БД она не нужна, потому что `001_create_base_schema.sql` уже создаёт актуальную integer-id структуру.

## Проверка после запуска миграций

### Проверить схему и справочники

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'arina'
ORDER BY table_name;
```

```sql
SELECT code, title, is_active
FROM arina.subjects
ORDER BY id;
```

```sql
SELECT class_number, title
FROM arina.school_classes
ORDER BY class_number;
```

```sql
SELECT s.code AS subject_code, t.class_number, COUNT(*) AS topics_count
FROM arina.topics t
JOIN arina.subjects s ON s.id = t.subject_id
GROUP BY s.code, t.class_number
ORDER BY s.code, t.class_number;
```

### Проверить русские словарные слова

```sql
SELECT class_number, COUNT(*) AS words_count
FROM arina.russian_vocabulary_words
GROUP BY class_number
ORDER BY class_number;
```

### Проверить английские слова

```sql
SELECT class_number, COUNT(*) AS words_count
FROM arina.english_vocabulary_words
GROUP BY class_number
ORDER BY class_number;
```

### Проверить темы 2 и 3 класса

```sql
SELECT s.code AS subject_code, t.class_number, COUNT(*) AS topics_count
FROM arina.topics t
JOIN arina.subjects s ON s.id = t.subject_id
WHERE t.class_number IN (2, 3)
GROUP BY s.code, t.class_number
ORDER BY s.code, t.class_number;
```

## Запуск через psql

Пример для Windows PowerShell:

```powershell
psql -U postgres -d arina_db -f database/migrations/001_create_base_schema.sql
psql -U postgres -d arina_db -f database/migrations/002_seed_subjects_classes_topics.sql
psql -U postgres -d arina_db -f database/migrations/004_create_russian_vocabulary_words.sql
psql -U postgres -d arina_db -f database/migrations/005_create_english_vocabulary_words.sql
psql -U postgres -d arina_db -f database/migrations/006_seed_class_2_topics.sql
psql -U postgres -d arina_db -f database/migrations/007_seed_class_3_topics.sql
```

## Что хранится в БД после миграций

```text
users
students
subjects
school_classes
topics
test_attempts
test_answers
account_activation_tokens
password_reset_tokens
password_history
russian_vocabulary_words
english_vocabulary_words
```

## Что остаётся в коде

В коде остаётся генерация заданий, логика проверки ответов, правила обучения и озвучка вопросов/слов.
