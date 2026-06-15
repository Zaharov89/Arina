import random
from typing import Any, Callable

from Arina.world.class_1_topics import WORLD_CLASS_1_TOPICS

MAX_UNIQUE_GENERATION_ATTEMPTS = 80


def get_topic_options_for_select() -> list[dict]:
    return [
        {"id": topic_id, "title": topic["title"], "short_title": topic.get("short_title", topic["title"])}
        for topic_id, topic in WORLD_CLASS_1_TOPICS.items()
    ]


def normalize_text(value: Any) -> str:
    return str(value).strip().lower().replace("ё", "е")


def normalize_question_text(question: str) -> str:
    return normalize_text(question)


def make_choice_task(question: str, choices: list[str], correct: str, topic: str | None = None) -> dict:
    return {
        "question": question,
        "answer_type": "choice",
        "choices": choices,
        "correct": correct,
        "topic": topic,
    }


def make_text_task(question: str, correct: str, topic: str | None = None) -> dict:
    return {
        "question": question,
        "answer_type": "text",
        "correct": correct,
        "topic": topic,
    }


def make_number_task(question: str, correct: int, topic: str | None = None) -> dict:
    return {
        "question": question,
        "answer_type": "number",
        "correct": correct,
        "topic": topic,
    }


def generate_unique_task(generator: Callable[[], dict], used_questions: list[str] | None = None) -> dict:
    used_normalized = {normalize_question_text(question) for question in (used_questions or [])}
    fallback_task = None

    for _ in range(MAX_UNIQUE_GENERATION_ATTEMPTS):
        task = generator()
        fallback_task = task
        question = normalize_question_text(task.get("question", ""))

        if not question or question not in used_normalized:
            task["is_repeat"] = False
            return task

    if fallback_task is None:
        fallback_task = generator()
    fallback_task["is_repeat"] = True
    return fallback_task


def generate_world_class_1_topic_task(topic_id: str, used_questions: list[str] | None = None) -> dict:
    generators = {
        "living_nonliving": generate_living_nonliving_task,
        "plants": generate_plants_task,
        "animals": generate_animals_task,
        "seasons": generate_seasons_task,
        "time": generate_time_task,
        "family_school": generate_family_school_task,
        "safety": generate_safety_task,
        "health": generate_health_task,
        "senses": generate_senses_task,
        "professions": generate_professions_task,
    }

    generator = generators.get(topic_id, generate_living_nonliving_task)
    task = generate_unique_task(generator, used_questions)
    task["topic"] = topic_id
    task["topic_title"] = WORLD_CLASS_1_TOPICS.get(topic_id, {}).get("title", "Окружающий мир 1 класс")
    return task


def generate_living_nonliving_task() -> dict:
    tasks = [
        make_choice_task("Что относится к живой природе?", ["кошка", "камень", "солнце"], "кошка", "living_nonliving"),
        make_choice_task("Что относится к неживой природе?", ["берёза", "рыба", "вода"], "вода", "living_nonliving"),
        make_choice_task("Выбери живой объект:", ["песок", "воробей", "воздух"], "воробей", "living_nonliving"),
        make_choice_task("Выбери неживой объект:", ["гриб", "трава", "камень"], "камень", "living_nonliving"),
        make_choice_task("Кто растёт, дышит и питается?", ["кошка", "камень", "солнце"], "кошка", "living_nonliving"),
    ]
    return random.choice(tasks)


def generate_plants_task() -> dict:
    tasks = [
        make_choice_task("Что нужно растению для жизни?", ["вода", "телевизор", "игрушка"], "вода", "plants"),
        make_choice_task("Что является деревом?", ["яблоня", "одуванчик", "трава"], "яблоня", "plants"),
        make_choice_task("Что является кустарником?", ["смородина", "берёза", "ромашка"], "смородина", "plants"),
        make_choice_task("Какая часть растения находится в земле?", ["корень", "цветок", "лист"], "корень", "plants"),
        make_text_task("Как называется зелёная часть растения?", "лист", "plants"),
    ]
    return random.choice(tasks)


def generate_animals_task() -> dict:
    tasks = [
        make_choice_task("Какое животное домашнее?", ["корова", "волк", "лиса"], "корова", "animals"),
        make_choice_task("Какое животное дикое?", ["кошка", "собака", "медведь"], "медведь", "animals"),
        make_choice_task("Кто относится к птицам?", ["воробей", "карась", "муравей"], "воробей", "animals"),
        make_choice_task("Кто относится к рыбам?", ["карась", "ворона", "заяц"], "карась", "animals"),
        make_text_task("Какое домашнее животное даёт молоко?", "корова", "animals"),
    ]
    return random.choice(tasks)


def generate_seasons_task() -> dict:
    tasks = [
        make_choice_task("Когда часто лежит снег?", ["зимой", "летом", "осенью"], "зимой", "seasons"),
        make_choice_task("Когда тает снег?", ["весной", "зимой", "летом"], "весной", "seasons"),
        make_choice_task("Когда часто опадают листья?", ["осенью", "весной", "летом"], "осенью", "seasons"),
        make_choice_task("Какой месяц зимний?", ["декабрь", "июнь", "сентябрь"], "декабрь", "seasons"),
        make_number_task("Сколько времён года в году?", 4, "seasons"),
    ]
    return random.choice(tasks)


def generate_time_task() -> dict:
    tasks = [
        make_number_task("Сколько дней в неделе?", 7, "time"),
        make_choice_task("Что идёт после понедельника?", ["вторник", "пятница", "суббота"], "вторник", "time"),
        make_choice_task("Когда обычно спят?", ["ночью", "утром", "днём"], "ночью", "time"),
        make_choice_task("Когда мы обычно завтракаем?", ["утром", "ночью", "вечером"], "утром", "time"),
        make_number_task("Сколько частей суток?", 4, "time"),
    ]
    return random.choice(tasks)


def generate_family_school_task() -> dict:
    tasks = [
        make_choice_task("Что относится к школе?", ["парта", "кастрюля", "подушка"], "парта", "family_school"),
        make_choice_task("Что нужно сделать, если хочешь ответить на уроке?", ["поднять руку", "кричать", "убежать"], "поднять руку", "family_school"),
        make_choice_task("Кто учит детей в школе?", ["учитель", "врач", "повар"], "учитель", "family_school"),
        make_choice_task("Как надо вести себя на уроке?", ["внимательно", "шумно", "грубо"], "внимательно", "family_school"),
        make_text_task("Как называется группа близких людей?", "семья", "family_school"),
    ]
    return random.choice(tasks)


def generate_safety_task() -> dict:
    tasks = [
        make_choice_task("На какой сигнал светофора можно переходить дорогу?", ["зелёный", "красный", "жёлтый"], "зелёный", "safety"),
        make_choice_task("Что означает красный сигнал светофора?", ["стой", "иди", "беги"], "стой", "safety"),
        make_choice_task("Где нельзя играть?", ["на проезжей части", "на площадке", "дома"], "на проезжей части", "safety"),
        make_choice_task("Можно ли брать спички без взрослых?", ["нет", "да"], "нет", "safety"),
        make_text_task("Какой свет светофора разрешает идти?", "зелёный", "safety"),
    ]
    return random.choice(tasks)


def generate_health_task() -> dict:
    tasks = [
        make_choice_task("Что нужно сделать перед едой?", ["вымыть руки", "побегать", "включить телевизор"], "вымыть руки", "health"),
        make_choice_task("Когда чистят зубы?", ["утром и вечером", "только зимой", "никогда"], "утром и вечером", "health"),
        make_choice_task("Что помогает быть здоровым?", ["зарядка", "грязные руки", "мало сна"], "зарядка", "health"),
        make_choice_task("Что полезнее?", ["яблоко", "много конфет"], "яблоко", "health"),
        make_text_task("Чем моют руки?", "мылом", "health"),
    ]
    return random.choice(tasks)


def generate_senses_task() -> dict:
    tasks = [
        make_choice_task("Чем мы видим?", ["глазами", "ушами", "носом"], "глазами", "senses"),
        make_choice_task("Чем мы слышим?", ["ушами", "языком", "руками"], "ушами", "senses"),
        make_choice_task("Чем мы чувствуем запах?", ["носом", "глазами", "ногами"], "носом", "senses"),
        make_choice_task("Чем мы чувствуем вкус?", ["языком", "ухом", "волосами"], "языком", "senses"),
        make_text_task("Какой орган помогает видеть?", "глаза", "senses"),
    ]
    return random.choice(tasks)


def generate_professions_task() -> dict:
    tasks = [
        make_choice_task("Кто лечит людей?", ["врач", "строитель", "водитель"], "врач", "professions"),
        make_choice_task("Кто учит детей?", ["учитель", "повар", "продавец"], "учитель", "professions"),
        make_choice_task("Кто готовит еду?", ["повар", "врач", "строитель"], "повар", "professions"),
        make_choice_task("Кто строит дома?", ["строитель", "учитель", "певец"], "строитель", "professions"),
        make_text_task("Как называется человек, который лечит людей?", "врач", "professions"),
    ]
    return random.choice(tasks)
