from Arina.russian_language.class_1_tasks import make_choice_task, generate_unique_task, normalize_text
from Arina.world.class_3_topics import WORLD_CLASS_3_TOPICS


def generate_world_class_3_topic_task(topic_id: str, used_questions: list[str] | None = None) -> dict:
    generators = {
        "earth_planet": lambda: make_choice_task("Земля вращается вокруг:", ["Солнца", "Луны", "Марса"], "Солнца", topic_id),
        "continents_oceans": lambda: make_choice_task("Что такое материк?", ["большой участок суши", "маленькая река", "облако"], "большой участок суши", topic_id),
        "map_globe": lambda: make_choice_task("Что является моделью Земли?", ["глобус", "термометр", "компас"], "глобус", topic_id),
        "water_cycle": lambda: make_choice_task("Что происходит с водой при нагревании?", ["испаряется", "становится камнем", "исчезает навсегда"], "испаряется", topic_id),
        "air_water_soil": lambda: make_choice_task("Что нужно растениям для роста?", ["почва", "пластик", "стекло"], "почва", topic_id),
        "plants_groups_3": lambda: make_choice_task("К какой группе относится берёза?", ["деревья", "кустарники", "травы"], "деревья", topic_id),
        "animals_groups_3": lambda: make_choice_task("Воробей относится к группе:", ["птицы", "рыбы", "насекомые"], "птицы", topic_id),
        "ecosystems_3": lambda: make_choice_task("Что является природным сообществом?", ["лес", "тетрадь", "стул"], "лес", topic_id),
        "human_body_3": lambda: make_choice_task("Какой орган помогает дышать?", ["лёгкие", "желудок", "ухо"], "лёгкие", topic_id),
        "healthy_lifestyle_3": lambda: make_choice_task("Что полезно для здоровья?", ["режим дня", "мало спать", "не двигаться"], "режим дня", topic_id),
        "russia_regions_3": lambda: make_choice_task("Россия — это:", ["многонациональная страна", "город", "океан"], "многонациональная страна", topic_id),
        "history_intro_3": lambda: make_choice_task("История изучает:", ["прошлое", "только погоду", "только растения"], "прошлое", topic_id),
        "ecology_rules_3": lambda: make_choice_task("Как нужно вести себя в природе?", ["бережно", "мусорить", "ломать деревья"], "бережно", topic_id),
    }
    generator = generators.get(topic_id, generators["earth_planet"])
    task = generate_unique_task(generator, used_questions)
    task["topic"] = topic_id
    task["topic_title"] = WORLD_CLASS_3_TOPICS.get(topic_id, {}).get("title", "Окружающий мир 3 класс")
    return task
