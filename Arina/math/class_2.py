import random

class MathExamplesClass2:
    def __init__(self, example_type, table_num):
        self.type = example_type
        self.table_num = table_num

    def generate_example(self):
        if self.type in ['all', 'addsub']:
            op = random.choice(['+', '-'])
        else:
            op = self.type

        if op == '+':
            # a, b от 0 до 100, но сумма строго <= 100
            a = random.randint(0, 100)
            b = random.randint(0, 100 - a)
        elif op == '-':
            # уменьшаемое a от 0 до 100, вычитаемое b от 0 до a, чтобы результат ≥ 0
            a = random.randint(0, 100)
            b = random.randint(0, a)
        else:
            # fallback, если когда-то появится другой знак
            a = random.randint(0, 100)
            b = random.randint(0, 100)

        return {'a': a, 'op': op, 'b': b}

    def calculate_answer(self, a, op, b):
        if op == '+': return a + b
        if op == '-': return a - b
