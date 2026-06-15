# Arina

Детское обучающее приложение для начальной школы.

В приложении сейчас есть:

- авторизация и регистрация пользователей;
- выбор предметов;
- обучение и тесты по математике, русскому языку и окружающему миру для 1 класса;
- словарные слова русского языка 1–3 класса из PostgreSQL;
- английский словарь 2–3 класса из PostgreSQL;
- дневник с оценками из PostgreSQL;
- контрольные срезы по предметам 1 класса.

## Технологии

- Python
- Flask
- PostgreSQL
- SQLAlchemy
- PyJWT
- pytest

## Быстрый запуск локально

### 1. Создать виртуальное окружение

PowerShell:

```powershell
python -m venv eduson_venv
.\eduson_venv\Scripts\Activate.ps1
```

или стандартный вариант:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Установить зависимости

```powershell
pip install -r requirements.txt
```

### 3. Создать базу данных PostgreSQL

Рекомендуемые параметры локальной БД:

```text
Host: localhost
Port: 5432
Database: arina_db
Schema: arina
Username: postgres
```

### 4. Настроить `.env`

В корне проекта создать файл `.env`:

```env
ARINA_DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/arina_db
ARINA_DATABASE_SCHEMA=arina
ARINA_JWT_SECRET=change-me-local-secret
ARINA_FLASK_HOST=127.0.0.1
ARINA_FLASK_PORT=5000
```

Пароль в `ARINA_DATABASE_URL` нужно заменить на свой пароль PostgreSQL.

### 5. Применить миграции

Миграции лежат здесь:

```text
database/migrations/
```

На чистой БД запускать в таком порядке:

```text
001_create_base_schema.sql
002_seed_subjects_classes_topics.sql
004_create_russian_vocabulary_words.sql
005_create_english_vocabulary_words.sql
```

Файл `003_rebuild_auth_tables_with_integer_ids.sql` — dev-only миграция для старого переходного этапа. На чистой БД он не нужен.

Через PowerShell и `psql`:

```powershell
psql -U postgres -d arina_db -f database/migrations/001_create_base_schema.sql
psql -U postgres -d arina_db -f database/migrations/002_seed_subjects_classes_topics.sql
psql -U postgres -d arina_db -f database/migrations/004_create_russian_vocabulary_words.sql
psql -U postgres -d arina_db -f database/migrations/005_create_english_vocabulary_words.sql
```

Через DBeaver можно открыть каждый SQL-файл и выполнить его через `Alt + X`.

### 6. Запустить приложение

```powershell
python -m Arina.app
```

После запуска открыть:

```text
http://127.0.0.1:5000
```

## Проверочные URL

```text
/database/status
/database/subjects
/database/school-classes
/database/topics
/api/russian/vocabulary?class_number=1
/api/english/vocabulary?class_number=2
/auth/login
/auth/register
/subjects
/diary
```

## Тесты

Запуск всех тестов:

```powershell
pytest
```

Smoke-тесты API находятся здесь:

```text
tests/test_api_smoke.py
```

Они проверяют базовые API-маршруты и авторизационные ответы без реального подключения к PostgreSQL.

## Сборка exe

Базовая команда PyInstaller:

```powershell
pyinstaller --onefile Arina/app.py
```

Если при сборке появятся ошибки скрытых импортов, добавляй их через `--hidden-import`.

## Где что хранится

### PostgreSQL

- пользователи;
- ученики;
- предметы;
- классы;
- темы;
- результаты тестов;
- ответы на задания;
- дневник;
- русские словарные слова;
- английские слова.

### Python-код

- генерация вопросов;
- проверка ответов;
- правила обучения;
- примеры к темам;
- озвучка вопросов и слов;
- отображение результатов.

## Важные API

```text
GET  /database/subjects
GET  /database/school-classes
GET  /database/topics?subject_code=math&class_number=1
GET  /api/russian/vocabulary?class_number=1
GET  /api/english/vocabulary?class_number=2
GET  /api/stats
POST /api/test-attempts
GET  /auth/me
```

`POST /api/save_result` удалён. Для сохранения результатов используется только:

```text
POST /api/test-attempts
```
