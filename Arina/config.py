import os


DEFAULT_STUDENT = "Арина"

FLASK_HOST = os.getenv("ARINA_FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("ARINA_FLASK_PORT", "5000"))
