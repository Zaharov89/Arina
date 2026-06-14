import random
from typing import Callable

from Arina.math.class_1_topics import CLASS_1_MATH_TOPICS


OBJECT_EMOJIS = ["🍎", "⭐", "🟦", "🐱", "🚗", "🎈", "🍬", "🌼"]
MAX_UNIQUE_GENERATION_ATTEMPTS = 120


def get_topic_options_for_select() -> list[dict]:
    return [
        {"id": topic_id, "title": topic["title"], "short_title": topic.get("short_title", topic["title"])}
        for topic_id, topic in CLASS_1_MATH_TOPICS.items()
    ]


def normalize_question_text(question: str) -> str:
    return str(question).strip().lower().replace("ё", "е")


def get_task_key(task: dict) -> str:
    question = str(task.get("question", "")).strip()
    choices = task.get("choices") or []
    if choices:
        return question + " | " + " | ".join(map(str, choices))
    return question


def attach_question_key(task: dict) -> dict:
    task["question_key"] = get_task_key(task)
    return task


def make_fallback_unique(task: dict, used_count: int) -> dict:
    task = dict(task)
    question = str(task.get("question", "Задание")).strip()
    task["question"] = f"{question} Задание {used_count + 1}."
    task["is_repeat"] = False
    return attach_question_key(task)


def generate_unique_task(generator: Callable[[], dict], used_questions: list[str] | None = None) -> dict:
    used_questions = used_questions or []
    used_normalized = {normalize_question_text(question) for question in used_questions}
    fallback_task = None

    for _ in range(MAX_UNIQUE_GENERATION_ATTEMPTS):
        task = attach_question_key(generator())
        fallback_task = task
        question_key = normalize_question_text(task.get("question_key", ""))

        if not question_key or question_key not in used_normalized:
            task["is_repeat"] = False
            return task

    if fallback_task is None:
        fallback_task = attach_question_key(generator())

    return make_fallback_unique(fallback_task, len(used_questions))


def generate_class_1_topic_task(topic_id: str, used_questions: list[str] | None = None) -> dict:
    generators = {
        "counting": generate_counting_task,
        "number_line": generate_number_line_task,
        "compare_numbers": generate_compare_numbers_task,
        "number_composition": generate_number_composition_task,
        "addition_to_10": generate_addition_to_10_task,
        "subtraction_to_10": generate_subtraction_to_10_task,
        "add_sub_to_20": generate_add_sub_to_20_task,
        "missing_number": generate_missing_number_task,
        "word_problems": generate_word_problem_task,
        "geometry": generate_geometry_task,
        "measurements": generate_measurement_task,
    }

    generator = generators.get(topic_id, generate_add_sub_to_20_task)
    task = generate_unique_task(generator, used_questions)
    task["topic"] = topic_id
    task["topic_title"] = CLASS_1_MATH_TOPICS.get(topic_id, {}).get("title", "Математика 1 класс")
    task["question_key"] = get_task_key(task)
    return task


def make_number_task(question: str, correct: int, topic: str | None = None) -> dict:
    return attach_question_key({"question": question, "answer_type": "number", "correct": correct, "topic": topic})


def make_choice_task(question: str, choices: list[str], correct: str, topic: str | None = None) -> dict:
    return attach_question_key({"question": question, "answer_type": "choice", "choices": choices, "correct": correct, "topic": topic})


def generate_counting_task() -> dict:
    count = random.randint(0, 10)
    emoji = random.choice(OBJECT_EMOJIS)
    objects = " ".join([emoji] * count) if count > 0 else "нет предметов"
    return make_number_task(f"Сколько предметов? {objects}", count, "counting")


def generate_number_line_task() -> dict:
    mode = random.choice(["next", "previous", "missing"])
    if mode == "next":
        number = random.randint(0, 49)
        return make_number_task(f"Какое число идёт после {number}?", number + 1, "number_line")
    if mode == "previous":
        number = random.randint(1, 50)
        return make_number_task(f"Какое число стоит перед {number}?", number - 1, "number_line")
    start = random.randint(0, 46)
    missing_offset = random.randint(1, 3)
    row = [start + i for i in range(5)]
    correct = row[missing_offset]
    row[missing_offset] = "?"
    return make_number_task("Какое число пропущено? " + ", ".join(map(str, row)), correct, "number_line")


def generate_compare_numbers_task() -> dict:
    left = random.randint(0, 50)
    right = random.randint(0, 50)
    correct = ">" if left > right else "<" if left < right else "="
    return make_choice_task(f"Поставь знак: {left} ? {right}", [">", "<", "="], correct, "compare_numbers")


def generate_number_composition_task() -> dict:
    total = random.randint(3, 20)
    first = random.randint(0, total)
    second = total - first
    if random.choice([True, False]):
        return make_number_task(f"{total} = {first} + ?", second, "number_composition")
    return make_number_task(f"{total} = ? + {second}", first, "number_composition")


def generate_addition_to_10_task() -> dict:
    a = random.randint(0, 10)
    b = random.randint(0, 10 - a)
    return make_number_task(f"{a} + {b} = ?", a + b, "addition_to_10")


def generate_subtraction_to_10_task() -> dict:
    a = random.randint(0, 10)
    b = random.randint(0, a)
    return make_number_task(f"{a} - {b} = ?", a - b, "subtraction_to_10")


def generate_add_sub_to_20_task() -> dict:
    op = random.choice(["+", "-"])
    if op == "+":
        a = random.randint(0, 20)
        b = random.randint(0, 20 - a)
        correct = a + b
    else:
        a = random.randint(0, 20)
        b = random.randint(0, a)
        correct = a - b
    return make_number_task(f"{a} {op} {b} = ?", correct, "add_sub_to_20")


def generate_missing_number_task() -> dict:
    mode = random.choice(["a_plus_missing", "missing_plus_b", "a_minus_missing", "missing_minus_b"])
    if mode == "a_plus_missing":
        a = random.randint(0, 20)
        missing = random.randint(0, max(0, 20 - a))
        return make_number_task(f"{a} + ? = {a + missing}", missing, "missing_number")
    if mode == "missing_plus_b":
        b = random.randint(0, 20)
        missing = random.randint(0, max(0, 20 - b))
        return make_number_task(f"? + {b} = {missing + b}", missing, "missing_number")
    if mode == "a_minus_missing":
        a = random.randint(1, 20)
        missing = random.randint(0, a)
        return make_number_task(f"{a} - ? = {a - missing}", missing, "missing_number")
    b = random.randint(0, 10)
    result = random.randint(0, 10)
    return make_number_task(f"? - {b} = {result}", result + b, "missing_number")


def generate_word_problem_task() -> dict:
    names = ["Маша", "Петя", "Арина", "Артём", "Ваня", "Оля"]
    objects = ["яблок", "конфет", "карандашей", "машинок", "кубиков", "шаров"]
    name = random.choice(names)
    obj = random.choice(objects)
    mode = random.choice(["add", "sub", "compare_more", "compare_less"])
    if mode == "add":
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        return make_number_task(f"У {name} было {a} {obj}. Ещё дали {b}. Сколько стало?", a + b, "word_problems")
    if mode == "sub":
        a = random.randint(2, 20)
        b = random.randint(1, a)
        return make_number_task(f"У {name} было {a} {obj}. {b} убрали. Сколько осталось?", a - b, "word_problems")
    if mode == "compare_more":
        a = random.randint(2, 20)
        b = random.randint(0, a - 1)
        return make_number_task(f"У {name} {a} {obj}, а у друга {b}. На сколько больше у {name}?", a - b, "word_problems")
    a = random.randint(0, 19)
    b = random.randint(a + 1, 20)
    return make_number_task(f"У {name} {a} {obj}, а у друга {b}. На сколько меньше у {name}?", b - a, "word_problems")


def generate_geometry_task() -> dict:
    tasks = [
        make_choice_task("У какой фигуры 3 стороны?", ["круг", "квадрат", "треугольник"], "треугольник", "geometry"),
        make_choice_task("У какой фигуры нет углов?", ["круг", "квадрат", "треугольник"], "круг", "geometry"),
        make_number_task("Сколько сторон у квадрата?", 4, "geometry"),
        make_number_task("Сколько углов у треугольника?", 3, "geometry"),
        make_choice_task("Какая фигура имеет 4 равные стороны?", ["круг", "квадрат", "треугольник"], "квадрат", "geometry"),
        make_choice_task("Как называется часть прямой с двумя концами?", ["круг", "отрезок", "квадрат"], "отрезок", "geometry"),
        make_choice_task("Что похоже на мяч?", ["шар", "куб", "отрезок"], "шар", "geometry"),
        make_choice_task("Что похоже на коробку?", ["куб", "круг", "линия"], "куб", "geometry"),
    ]
    return random.choice(tasks)


def generate_measurement_task() -> dict:
    conversions = [(1, 10), (2, 20), (3, 30), (4, 40), (5, 50)]
    amount, cm = random.choice(conversions)
    tasks = [
        make_number_task(f"{amount} дм = ? см", cm, "measurements"),
        make_choice_task("В чём измеряют длину линейки?", ["сантиметры", "килограммы", "литры"], "сантиметры", "measurements"),
        make_choice_task("В чём измеряют массу арбуза?", ["литры", "килограммы", "сантиметры"], "килограммы", "measurements"),
        make_choice_task("В чём измеряют молоко?", ["литры", "килограммы", "сантиметры"], "литры", "measurements"),
        make_choice_task("В чём измеряют воду?", ["литры", "метры", "килограммы"], "литры", "measurements"),
        make_choice_task("В чём измеряют длину стола?", ["сантиметры", "литры", "килограммы"], "сантиметры", "measurements"),
    ]
    return random.choice(tasks)
