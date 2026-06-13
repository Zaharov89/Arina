import os


DEFAULT_STUDENT = "Арина"

FLASK_HOST = os.getenv("ARINA_FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("ARINA_FLASK_PORT", "5000"))

# Оставил fallback на текущий URL, чтобы после замены код продолжил работать без настройки env.
# Позже лучше убрать fallback и хранить URL только в переменной окружения.
GOOGLE_SCRIPT_URL = os.getenv(
    "ARINA_GOOGLE_SCRIPT_URL",
    "https://script.google.com/macros/s/AKfycbwSw2z5nGJ-GQhtCzkYM8cKLy8WOFM47IyY0ahUi3JJDe1y-m4vZKOW_mnzCnMk3Dm7/exec",
)