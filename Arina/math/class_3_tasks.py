import random

from Arina.math.class_3_topics import CLASS_3_MATH_TOPICS
from Arina.utils.safe_math import safe_eval_math_expr, SafeMathExpressionError


def topic_title(topic: str) -> str:
    return CLASS_3_MATH_TOPICS.get(topic, {}).get("title") or CLASS_3_MATH_TOPICS.get(topic, {}).get("description") or "Математика 3 класс"


def number_task(question: str, correct: int, topic: str) -> dict:
    return {"question": question, "answer_type": "number", "correct": correct, "topic": topic, "topic_title": topic_title(topic)}


def choice_task(question: str, choices: list[str], correct: str, topic: str) -> dict:
    return {"question": question, "answer_type": "choice", "choices": choices, "correct": correct, "topic": topic, "topic_title": topic_title(topic)}


def generate_math_class_3_topic_task(topic_id: str) -> dict:
    generators = {
        "numbers_to_1000": generate_numbers_to_1000,
        "compare_to_1000": generate_compare_to_1000,
        "add_sub_to_1000": generate_add_sub_to_1000,
        "multiplication_division_table": generate_multiplication_division_table,
        "multiply_divide_by_10_100": generate_multiply_divide_by_10_100,
        "division_with_remainder": generate_division_with_remainder,
        "order_of_operations_3": generate_order_of_operations,
        "equations_3": generate_equation,
        "word_problems_3": generate_word_problem,
        "measurements_3": generate_measurements,
        "area_perimeter": generate_area_perimeter,
        "fractions_intro": generate_fractions_intro,
    }
    return generators.get(topic_id, generate_numbers_to_1000)()


def generate_numbers_to_1000() -> dict:
    n = random.randint(100, 999)
    hundreds = n // 100
    tens = (n % 100) // 10
    ones = n % 10
    return random.choice([
        number_task(f"Сколько сотен в числе {n}?", hundreds, "numbers_to_1000"),
        number_task(f"Сколько десятков в числе {n}?", tens, "numbers_to_1000"),
        number_task(f"Сколько единиц в числе {n}?", ones, "numbers_to_1000"),
    ])


def generate_compare_to_1000() -> dict:
    a, b = random.sample(range(100, 1000), 2)
    correct = ">" if a > b else "<"
    return choice_task(f"Какой знак нужен: {a} __ {b}?", [">", "<", "="], correct, "compare_to_1000")


def generate_add_sub_to_1000() -> dict:
    if random.choice([True, False]):
        a = random.randint(100, 800)
        b = random.randint(10, 1000 - a)
        return {"a": a, "op": "+", "b": b, "answer_type": "number", "correct": a + b, "topic": "add_sub_to_1000", "topic_title": topic_title("add_sub_to_1000")}
    a = random.randint(150, 1000)
    b = random.randint(10, a)
    return {"a": a, "op": "-", "b": b, "answer_type": "number", "correct": a - b, "topic": "add_sub_to_1000", "topic_title": topic_title("add_sub_to_1000")}


def generate_multiplication_division_table() -> dict:
    a, b = random.randint(2, 10), random.randint(2, 10)
    if random.choice([True, False]):
        return {"a": a, "op": "*", "b": b, "answer_type": "number", "correct": a * b, "topic": "multiplication_division_table", "topic_title": topic_title("multiplication_division_table")}
    product = a * b
    return {"a": product, "op": "/", "b": a, "answer_type": "number", "correct": b, "topic": "multiplication_division_table", "topic_title": topic_title("multiplication_division_table")}


def generate_multiply_divide_by_10_100() -> dict:
    n = random.randint(2, 90)
    factor = random.choice([10, 100])
    if random.choice([True, False]):
        return {"a": n, "op": "*", "b": factor, "answer_type": "number", "correct": n * factor, "topic": "multiply_divide_by_10_100", "topic_title": topic_title("multiply_divide_by_10_100")}
    return {"a": n * factor, "op": "/", "b": factor, "answer_type": "number", "correct": n, "topic": "multiply_divide_by_10_100", "topic_title": topic_title("multiply_divide_by_10_100")}


def generate_division_with_remainder() -> dict:
    divisor = random.randint(2, 9)
    quotient = random.randint(2, 9)
    remainder = random.randint(1, divisor - 1)
    dividend = divisor * quotient + remainder
    return choice_task(f"Какой остаток при делении {dividend} : {divisor}?", [str(remainder), str((remainder + 1) % divisor), "0"], str(remainder), "division_with_remainder")


def generate_order_of_operations() -> dict:
    a, b, c = random.randint(2, 20), random.randint(2, 9), random.randint(2, 9)
    expr = f"{a} + {b} * {c}"
    try:
        correct = safe_eval_math_expr(expr)
    except SafeMathExpressionError:
        correct = a + b * c
    return {"expr": expr, "answer_type": "number", "correct": correct, "topic": "order_of_operations_3", "topic_title": topic_title("order_of_operations_3")}


def generate_equation() -> dict:
    x = random.randint(2, 60)
    b = random.randint(2, 40)
    return {"question": f"x + {b} = {x + b}", "answer_type": "number", "correct": x, "topic": "equations_3", "topic_title": topic_title("equations_3")}


def generate_word_problem() -> dict:
    packs = random.randint(2, 8)
    per_pack = random.randint(3, 9)
    extra = random.randint(2, 20)
    return number_task(f"Купили {packs} пачки по {per_pack} тетрадей и ещё {extra} тетрадей. Сколько всего тетрадей?", packs * per_pack + extra, "word_problems_3")


def generate_measurements() -> dict:
    return random.choice([
        number_task("Сколько метров в 1 километре?", 1000, "measurements_3"),
        number_task("Сколько граммов в 1 килограмме?", 1000, "measurements_3"),
        number_task("Сколько минут в 2 часах?", 120, "measurements_3"),
    ])


def generate_area_perimeter() -> dict:
    a, b = random.randint(2, 12), random.randint(2, 12)
    if random.choice([True, False]):
        return number_task(f"Найди площадь прямоугольника со сторонами {a} см и {b} см.", a * b, "area_perimeter")
    return number_task(f"Найди периметр прямоугольника со сторонами {a} см и {b} см.", 2 * (a + b), "area_perimeter")


def generate_fractions_intro() -> dict:
    return random.choice([
        choice_task("Как называется одна из двух равных частей?", ["половина", "треть", "четверть"], "половина", "fractions_intro"),
        choice_task("Как записать половину?", ["1/2", "1/3", "2/1"], "1/2", "fractions_intro"),
    ])
