# Frontend

HTML и CSS теперь живут во frontend-зоне проекта:

```text
Arina/frontend/templates/
Arina/frontend/static/
```

Flask настроен на эти папки в:

```text
Arina/backend/app_factory.py
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

Если после переноса страница открывается без CSS или с 404 по шаблону, сначала проверь, что файл лежит именно в этих папках.
