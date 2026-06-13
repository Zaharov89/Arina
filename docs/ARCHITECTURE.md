# Архитектура проекта Arina

Текущий рефакторинг разбивает проект на зоны ответственности, но сохраняет старые рабочие URL.

## Основные зоны

```text
Arina/
  app.py                 # тонкая точка входа для запуска приложения
  backend/               # Flask app factory, routes, services
  auth/                  # будущая регистрация, авторизация, активация через email
  database/              # будущий PostgreSQL слой
  frontend/              # HTML-шаблоны и CSS/static assets
  stats/                 # текущая интеграция чтения дневника из Google Apps Script
```

## Backend

```text
Arina/backend/
  app_factory.py
  routes/
    pages.py             # /, /subjects, /student_selection
    english.py           # /english/*
    russian.py           # /russian/*
    math.py              # /math/*, /generate_example, /check_answer
    results.py           # /results/*
    vocabulary_api.py    # /questions
  services/
    result_storage.py    # будущая логика сохранения результатов
```

`Arina/backend/app_factory.py` создаёт Flask-приложение и указывает Flask на frontend-папки:

```text
Arina/frontend/templates/
Arina/frontend/static/
```

## Auth

```text
Arina/auth/
  routes.py              # /auth/status, /auth/register, /auth/login, /auth/activate/<token>
  services.py            # будущая логика email-активации и токенов
```

Сейчас auth endpoints являются заглушками и возвращают JSON со статусом `planned` или HTTP 501.

## Database

```text
Arina/database/
  config.py              # будущий DATABASE_URL
  routes.py              # /database/status
  models.py              # будущие SQLAlchemy models
  repositories.py        # будущий слой доступа к данным
```

## Frontend

HTML/CSS теперь находятся здесь:

```text
Arina/frontend/templates/
Arina/frontend/static/
```

Ожидаемая структура:

```text
Arina/frontend/templates/
  index.html
  subjects.html
  diary/diary.html
  math/
  russian/
  english/
  results/

Arina/frontend/static/
  shared.css
  diary/
  math/
  russian/
  english/
  results/
  img/
```

## Сохранённые URL

Пользовательские URL не изменены:

```text
/
/subjects
/student_selection
/math
/math/test_setup
/math/test
/russian
/russian/rules
/russian/test_setup
/russian/test
/english/menu
/english/vocabulary
/english/rules
/english/test_setup
/english/test
/results/math
/results/russian
/results/english
/diary
/stats
/api/stats
/api/save_result
/questions
```

Новые архитектурные URL:

```text
/auth/status
/auth/register
/auth/login
/auth/activate/<token>
/database/status
```
