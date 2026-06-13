import random

from Arina.math.class_1_tasks import generate_class_1_topic_task
from Arina.math.class_1_topics import CLASS_1_MATH_TOPICS


class MathExamplesClass1:
    def __init__(self, example_type, table_num):
        self.type = example_type
        self.table_num = table_num

    def generate_example(self):
        if self.type in CLASS_1_MATH_TOPICS:
            return generate_class_1_topic_task(self.type)

        if self.type == "addition_to_10":
            return generate_class_1_topic_task("addition_to_10")

        if self.type == "subtraction_to_10":
            return generate_class_1_topic_task("subtraction_to_10")

        if self.type in ["all", "addsub"]:
            op = random.choice(["+", "-"])
        else:
            op = self.type

        if op == "+":
            # a, b от 0 до 20, но сумма строго <= 20
            a = random.randint(0, 20)
            b = random.randint(0, 20 - a)
        elif op == "-":
            # уменьшаемое a от 0 до 20, вычитаемое b от 0 до a, чтобы результат ≥ 0
            a = random.randint(0, 20)
            b = random.randint(0, a)
        else:
            # fallback, если когда-то появится другой знак
            a = random.randint(0, 20)
            b = random.randint(0, 20)

        return {"a": a, "op": op, "b": b}

    def calculate_answer(self, a, op, b):
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        return None
