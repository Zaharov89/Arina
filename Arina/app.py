import subprocess
import sys
import threading
import time

# === ЯВНЫЕ ИМПОРТЫ ДЛЯ PYINSTALLER (НЕ УДАЛЯТЬ!) ===
import Arina.russian_language.class_1_tasks
import Arina.russian_language.class_1_topics
import Arina.russian_language.class_2_tasks
import Arina.russian_language.class_2_topics
import Arina.russian_language.vocabulary
import Arina.english_language.class_2_tasks
import Arina.english_language.class_2_topics
import Arina.english_language.vocabulary
import Arina.math.class_1
import Arina.math.class_1_tasks
import Arina.math.class_1_topics
import Arina.math.class_2
import Arina.math.class_2_topics
import Arina.math.class_3
import Arina.world.class_1_tasks
import Arina.world.class_1_topics
import Arina.world.class_2_tasks
import Arina.world.class_2_topics
import Arina.utils.safe_math
# ===================================================

from Arina.backend.app_factory import create_app, get_run_config


app = create_app()


def run_flask():
    host, port = get_run_config()
    app.run(debug=False, host=host, port=port)


def open_browser():
    time.sleep(2)
    host, port = get_run_config()
    url = f"http://{host}:{port}"

    if sys.platform == "win32":
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        try:
            subprocess.Popen([chrome_path, "--new-window", url])
        except FileNotFoundError:
            subprocess.Popen(["cmd", "/c", "start", "", url], shell=True)

    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-n", "-a", "Google Chrome", url])

    else:
        subprocess.Popen(["xdg-open", url])


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    open_browser()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
