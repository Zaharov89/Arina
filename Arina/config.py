import os


DEFAULT_STUDENT = "Арина"

FLASK_HOST = os.getenv("ARINA_FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("ARINA_FLASK_PORT", "5000"))

LOG_LEVEL = os.getenv("ARINA_LOG_LEVEL", "INFO")
LOG_TO_FILE = os.getenv("ARINA_LOG_TO_FILE", "true").lower() in {"1", "true", "yes", "on"}
LOG_DIR = os.getenv("ARINA_LOG_DIR", os.path.join(os.getcwd(), "logs"))
