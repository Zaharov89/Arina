import random

from Arina.math.class_2_topics import CLASS_2_MATH_TOPICS


class MathExamplesClass2:
    def __init__(self, example_type, table_num='all', used_questions=None):
        self.type = example_type or 'numbers_to_100'
        self.table_num = table_num
        self.used_questions = used_questions or []

    def topic_title(self, topic: str) -> str:
        return CLASS_2_MATH_TOPICS.get(topic, {}).get('title') or CLASS_2_MATH_TOPICS.get(topic, {}).get('description') or 'Математика 2 класс'

    def generate_example(self):
        generators = {
            'numbers_to_100': self.generate_numbers_to_100,
            'compare_to_100': self.generate_compare_to_100,
            'add_sub_no_crossing': self.generate_add_sub_no_crossing,
            'add_sub_crossing': self.generate_add_sub_crossing,
            'addition_table': self.generate_addition_table,
            'multiplication_table': self.generate_multiplication_table,
            'division_equal_parts': self.generate_division_equal_parts,
            'mul_div_relation': self.generate_mul_div_relation,
            'word_problems_2': self.generate_word_problem,
            'measurements_2': self.generate_measurements,
            'geometry_perimeter': self.generate_geometry_perimeter,
            'parentheses_2': self.generate_parentheses,
            'all': self.generate_add_sub_crossing,
            'addsub': self.generate_add_sub_crossing,
            '+': self.generate_add_sub_crossing,
            '-': self.generate_add_sub_crossing,
        }
        topic = self.type if self.type in CLASS_2_MATH_TOPICS else 'numbers_to_100'
        task = generators.get(self.type, self.generate_numbers_to_100)()
        task.setdefault('topic', topic)
        task.setdefault('topic_title', self.topic_title(topic))
        return task

    @staticmethod
    def calculate_answer(a, op, b):
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '*': return a * b
        if op == '/': return a // b if b else None
        return None

    def number_task(self, question, correct, topic):
        return {'question': question, 'answer_type': 'number', 'correct': correct, 'topic': topic, 'topic_title': self.topic_title(topic)}

    def choice_task(self, question, choices, correct, topic):
        return {'question': question, 'answer_type': 'choice', 'choices': choices, 'correct': correct, 'topic': topic, 'topic_title': self.topic_title(topic)}

    def generate_numbers_to_100(self):
        n = random.randint(10, 99)
        tens, ones = divmod(n, 10)
        return random.choice([
            self.number_task(f'Сколько десятков в числе {n}?', tens, 'numbers_to_100'),
            self.number_task(f'Сколько единиц в числе {n}?', ones, 'numbers_to_100'),
            self.number_task(f'Какое число идёт после {n}?', n + 1 if n < 99 else 100, 'numbers_to_100'),
        ])

    def generate_compare_to_100(self):
        a, b = random.sample(range(10, 100), 2)
        correct = '>' if a > b else '<'
        return self.choice_task(f'Какой знак нужен: {a} __ {b}?', ['>', '<', '='], correct, 'compare_to_100')

    def generate_add_sub_no_crossing(self):
        tens1, ones1 = random.randint(1, 8), random.randint(0, 8)
        tens2, ones2 = random.randint(1, 9 - tens1), random.randint(0, 9 - ones1)
        a, b = tens1 * 10 + ones1, tens2 * 10 + ones2
        if random.choice([True, False]):
            return {'a': a, 'op': '+', 'b': b, 'topic': 'add_sub_no_crossing', 'topic_title': self.topic_title('add_sub_no_crossing')}
        total = a + b
        return {'a': total, 'op': '-', 'b': b, 'topic': 'add_sub_no_crossing', 'topic_title': self.topic_title('add_sub_no_crossing')}

    def generate_add_sub_crossing(self):
        op = '+' if self.type not in {'-'} else '-'
        if self.type == '+': op = '+'
        elif self.type == '-': op = '-'
        elif self.type in {'all', 'addsub', 'add_sub_crossing'}: op = random.choice(['+', '-'])
        if op == '+':
            a = random.randint(15, 89)
            b = random.randint(6, min(20, 100 - a))
        else:
            a = random.randint(20, 100)
            b = random.randint(6, min(30, a))
        return {'a': a, 'op': op, 'b': b, 'topic': 'add_sub_crossing', 'topic_title': self.topic_title('add_sub_crossing')}

    def generate_addition_table(self):
        a, b = random.randint(2, 9), random.randint(2, 9)
        return {'a': a, 'op': '+', 'b': b, 'topic': 'addition_table', 'topic_title': self.topic_title('addition_table')}

    def generate_multiplication_table(self):
        a, b = random.randint(2, 5), random.randint(2, 10)
        return {'a': a, 'op': '*', 'b': b, 'topic': 'multiplication_table', 'topic_title': self.topic_title('multiplication_table')}

    def generate_division_equal_parts(self):
        b = random.randint(2, 5)
        q = random.randint(2, 10)
        a = b * q
        return {'a': a, 'op': '/', 'b': b, 'topic': 'division_equal_parts', 'topic_title': self.topic_title('division_equal_parts')}

    def generate_mul_div_relation(self):
        a, b = random.randint(2, 5), random.randint(2, 10)
        product = a * b
        return random.choice([
            self.number_task(f'Если {a} × {b} = {product}, чему равно {product} : {a}?', b, 'mul_div_relation'),
            self.number_task(f'Если {a} × {b} = {product}, чему равно {product} : {b}?', a, 'mul_div_relation'),
        ])

    def generate_word_problem(self):
        a, b = random.randint(10, 40), random.randint(5, 30)
        if a < b: a, b = b, a
        return random.choice([
            self.number_task(f'У Маши было {a} наклеек, ей подарили ещё {b}. Сколько стало?', a + b, 'word_problems_2'),
            self.number_task(f'В коробке было {a} карандашей, {b} взяли. Сколько осталось?', a - b, 'word_problems_2'),
        ])

    def generate_measurements(self):
        return random.choice([
            self.number_task('Сколько сантиметров в 1 метре?', 100, 'measurements_2'),
            self.number_task('Сколько минут в 1 часе?', 60, 'measurements_2'),
            self.number_task('Сколько месяцев в 1 году?', 12, 'measurements_2'),
        ])

    def generate_geometry_perimeter(self):
        a, b = random.randint(2, 10), random.randint(2, 10)
        return self.number_task(f'Найди периметр прямоугольника со сторонами {a} см и {b} см.', 2 * (a + b), 'geometry_perimeter')

    def generate_parentheses(self):
        a, b, c = random.randint(2, 20), random.randint(2, 20), random.randint(2, 20)
        return {'expr': f'({a} + {b}) - {c}', 'correct': a + b - c, 'answer_type': 'number', 'topic': 'parentheses_2', 'topic_title': self.topic_title('parentheses_2')}
