# Frontend

Сейчас HTML и CSS остаются в проверенных рабочих папках:

```text
Arina/templates/
Arina/static/
```

Это сделано специально, чтобы не сломать рабочие шаблоны, картинки и CSS при первом архитектурном рефакторинге.

План на следующий этап:

```text
Arina/frontend/templates/
Arina/frontend/static/
```

После переноса всех HTML/CSS/изображений нужно будет обновить `template_folder` и `static_folder` в `Arina/backend/app_factory.py`.
