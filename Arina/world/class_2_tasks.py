from Arina.russian_language.class_1_tasks import make_choice_task, generate_unique_task, normalize_text
from Arina.world.class_2_topics import WORLD_CLASS_2_TOPICS


def generate_world_class_2_topic_task(topic_id: str, used_questions: list[str] | None = None) -> dict:
    generators = {
        "nature_living_nonliving_2": lambda: make_choice_task("Что относится к живой природе?", ["берёза", "камень", "солнце"], "берёза", topic_id),
        "natural_phenomena": lambda: make_choice_task("Что является явлением природы?", ["дождь", "стул", "тетрадь"], "дождь", topic_id),
        "seasons_weather_2": lambda: make_choice_task("После зимы наступает:", ["весна", "осень", "лето"], "весна", topic_id),
        "plants_2": lambda: make_choice_task("Что нужно растению для жизни?", ["свет", "пластик", "камень"], "свет", topic_id),
        "animals_2": lambda: make_choice_task("Какое животное дикое?", ["волк", "корова", "кошка"], "волк", topic_id),
        "human_health_2": lambda: make_choice_task("Что полезно для здоровья?", ["зарядка", "мало спать", "есть только конфеты"], "зарядка", topic_id),
        "senses_2": lambda: make_choice_task("Какой орган помогает слышать?", ["ухо", "глаз", "нос"], "ухо", topic_id),
        "safety_2": lambda: make_choice_task("Где правильно переходить дорогу?", ["по переходу", "где удобно", "между машинами"], "по переходу", topic_id),
        "family_society": lambda: make_choice_task("Кто учит детей в школе?", ["учитель", "врач", "повар"], "учитель", topic_id),
        "hometown": lambda: make_choice_task("Как называется главный город страны?", ["столица", "улица", "деревня"], "столица", topic_id),
        "russia_symbols": lambda: make_choice_task("Столица России — это:", ["Москва", "Париж", "Берлин"], "Москва", topic_id),
        "professions_2": lambda: make_choice_task("Кто лечит людей?", ["врач", "пилот", "строитель"], "врач", topic_id),
        "ecology_2": lambda: make_choice_task("Как нужно относиться к природе?", ["бережно", "мусорить", "ломать ветки"], "бережно", topic_id),
    }
    generator = generators.get(topic_id, generators["nature_living_nonliving_2"])
    task = generate_unique_task(generator, used_questions)
    task["topic"] = topic_id
    task["topic_title"] = WORLD_CLASS_2_TOPICS.get(topic_id, {}).get("title", "Окружающий мир 2 класс")
    return task
