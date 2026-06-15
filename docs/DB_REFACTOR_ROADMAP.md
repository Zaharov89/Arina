# План рефакторинга данных Arina

Документ фиксирует, какие данные должны жить в PostgreSQL, что остаётся в Python-коде, какие API нужны и в каком порядке безопасно убирать дубли.

## Хранить в БД

### Уже нужно хранить в БД

1. **Классы**
   - Таблица: `arina.school_classes`.
   - Данные: 1–11 класс.
   - API: `GET /database/school-classes`.

2. **Пользователи**
   - Таблица: `arina.users`.
   - Данные: email, password_hash, first_name, last_name, is_active, is_admin.
   - Связанные ученики: `arina.students`.
   - API: auth endpoints, далее нужен отдельный `GET /api/students`.

3. **Школьные предметы**
   - Таблица: `arina.subjects`.
   - Данные: math, russian, world, english.
   - API: `GET /database/subjects`.

4. **Темы по предметам и классам**
   - Таблица: `arina.topics`.
   - Данные: subject_id, class_number, code, title, is_active.
   - API: `GET /database/topics?subject_code=math&class_number=1`.
   - Важно: генерация заданий остаётся в Python, но названия тем и список тем должны браться из БД.

5. **Оценки за задания по предметам**
   - Таблицы: `arina.test_attempts`, `arina.test_answers`.
   - Данные: ученик, предмет, класс, тема, количество заданий, правильные/ошибочные/пустые ответы, процент, оценка, время.
   - Нужные API:
     - `POST /api/test-attempts`
     - `GET /api/test-attempts?student_id=...`
     - `GET /api/test-attempts/<attempt_id>`

6. **Оценки и средний балл для дневника**
   - Нужны таблицы дневника, например:
     - `arina.diary_grades`
     - `arina.diary_summary` или view/materialized view для среднего балла.
   - Нужные API:
     - `GET /api/diary?student_id=...`
     - `POST /api/diary/grades`
     - `GET /api/diary/summary?student_id=...`

7. **Словарные слова по русскому языку для каждого класса отдельно**
   - Нужна таблица: `arina.russian_vocabulary_words`.
   - Поля: id, class_number, word, is_active, created_at.
   - Нужные API:
     - `GET /api/russian/vocabulary?class_number=1`
     - `GET /api/russian/vocabulary?class_number=2`
     - `GET /api/russian/vocabulary?class_number=3`
   - Отдельная задача: проверить школьную программу и разделить текущие слова 2 класса на 1 и 2 класс.

8. **Слова для заучивания по английскому языку**
   - Нужна таблица: `arina.english_vocabulary_words`.
   - Поля: id, class_number, english_word, russian_translation, transcription, is_active, created_at.
   - Нужные API:
     - `GET /api/english/vocabulary?class_number=2`
     - `GET /api/english/vocabulary?class_number=3`

## Оставить в коде

1. Генерацию вопросов и ответов по всем предметам.
2. Подключение голоса к вопросам и правилам.
3. Подключение голоса к английским словам в вопросах.
4. Вывод результатов после тестирования.
5. Логику проверки ответа и генераторы по `topic_code`.

## Удалить из кода

1. Всё, что связано с Google Таблицами и Google Apps Script:
   - `GOOGLE_SCRIPT_URL` из `Arina/config.py`.
   - Запросы `requests.get(...)` к Google в `Arina/stats/routes.py`.
   - Старую заглушку `/api/save_result`, когда будет готов `POST /api/test-attempts`.
2. Дублирующие списки предметов, классов, тем и слов, когда соответствующие таблицы и API будут готовы.

## Что уже найдено в main

### Google Sheets

В `Arina/stats/routes.py` всё ещё есть зависимость от Google Apps Script:

- импортируется `GOOGLE_SCRIPT_URL`;
- используется `requests.get(GOOGLE_SCRIPT_URL, ...)`;
- `/api/stats` получает дневник из Google;
- `/api/save_result` пока является заглушкой.

В `Arina/config.py` всё ещё есть `GOOGLE_SCRIPT_URL`.

### Дубли справочников

1. В `subjects.html` был захардкожен список предметов, хотя есть таблица `arina.subjects`.
2. В `math/class_1_topics.py`, `russian_language/class_1_topics.py`, `world/class_1_topics.py` хранятся темы, описания, правила и примеры.
3. Словарные слова русского и английского пока живут в Python-файлах, их нужно вынести в БД.

## Безопасный порядок работ

### Ветка 1: `feature/catalog-ui-update`

- Переделать страницу восстановления пароля.
- Добавить GET API для справочников:
  - `/database/subjects`
  - `/database/school-classes`
  - `/database/topics`
- Перевести страницу `/subjects` на данные из `arina.subjects`.

### Ветка 2: `feature/db-driven-topics`

- Перевести страницы выбора тем по математике, русскому и окружающему миру на `GET /database/topics`.
- В Python оставить только mapping `topic_code -> generator`.
- Убрать дублирующие списки title/code из topic-файлов.

### Ветка 3: `feature/russian-vocabulary-db`

- Создать таблицу `arina.russian_vocabulary_words`.
- Разделить словарные слова русского языка по классам.
- Добавить API `GET /api/russian/vocabulary?class_number=...`.
- Перевести диктанты/словарик на БД.

### Ветка 4: `feature/english-vocabulary-db`

- Создать таблицу `arina.english_vocabulary_words`.
- Перенести английские слова и переводы в БД.
- Добавить API `GET /api/english/vocabulary?class_number=...`.
- Перевести английский словарик и тесты слов на БД.

### Ветка 5: `feature/postgres-diary`

- Создать таблицы дневника.
- Перенести `/api/stats` на PostgreSQL.
- Удалить Google Apps Script из `Arina/stats/routes.py`.
- Удалить `GOOGLE_SCRIPT_URL` из `Arina/config.py`.

### Ветка 6: `feature/test-attempts-api`

- Реализовать сохранение результатов тестирования в PostgreSQL.
- Добавить `POST /api/test-attempts`.
- Подключить фронт результатов к новому API.
- Удалить старую заглушку `/api/save_result`.

## Что ещё нужно добавить в список БД

Дополнительно к твоему списку стоит хранить в БД:

1. **Темы предметов по классам** — уже есть `arina.topics`, но нужно использовать её в коде полностью.
2. **Историю ответов ученика** — уже заложено в `arina.test_answers`.
3. **Настройки пользователя/ученика** — позже может понадобиться отдельная таблица, например `arina.student_settings`.
4. **Статусы активности справочников** — уже есть `is_active` у subjects/topics; то же нужно у vocabulary words.
5. **Миграции БД** — все изменения схемы должны оформляться SQL-файлами в `database/migrations`.
