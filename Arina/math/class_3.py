import random


class MathExamplesClass3:
    def __init__(self, example_type, table_num):
        self.type = example_type
        self.table_num = table_num

    def generate_example(self):
        if self.type == 'simple_equation':
            return self.generate_simple_equation()
        elif self.type == 'parentheses':
            return self.generate_parentheses_example()
        # Обычные примеры
        if self.type in ['all']:
            ops = ['+', '-', '*', '/']
        elif self.type == 'addsub':
            ops = ['+', '-']
        elif self.type == 'muldiv':
            ops = ['*', '/']
        else:
            ops = [self.type]
        while True:
            op = random.choice(ops)
            if op in ['*', '/']:
                a = random.randint(0, 10)
                b = random.randint(1, 10)
                if op == '/':
                    result = random.randint(0, 10)
                    a = result * b
                    res = a // b
                else:  # '*'
                    res = a * b
            else:  # плюс/минус только от 0 до 100
                if op == '+':
                    a = random.randint(0, 100)
                    b = random.randint(0, 100 - a)
                    res = a + b
                else:  # '-'
                    a = random.randint(0, 100)
                    b = random.randint(0, a)
                    res = a - b
            if 0 <= res <= (100 if op in '+-' else 100):
                return {'a': a, 'op': op, 'b': b}

    def calculate_answer(self, a, op, b):
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '*': return a * b
        if op == '/': return a // b

    def generate_simple_equation(self, allowed_ops=None):
        ops = allowed_ops if allowed_ops else ['+', '-']
        ops = [op for op in ops if op in ['+', '-']]
        if not ops:
            ops = ['+']
        while True:
            op = random.choice(ops)
            if op == '+':
                x = random.randint(1, 50)
                b = random.randint(1, 50)
                result = x + b
                if result <= 100:
                    return {'type': 'simple_equation', 'question': f'x + {b} = {result}', 'x': x}
            else:  # '-'
                result = random.randint(1, 50)
                x = random.randint(1, 50)
                a = result + x
                if a <= 100:
                    return {'type': 'simple_equation', 'question': f'{a} - x = {result}', 'x': x}

    def solve_simple_equation(self, expr_dict, user_x):
        return int(user_x) == expr_dict['x']

    def generate_parentheses_example(self, allowed_ops=None):
        ops = allowed_ops if allowed_ops else ['+', '-', '*', '/']

        def rand_sum():
            a = random.randint(0, 100)
            b = random.randint(0, 100 - a)
            return a, '+', b

        def rand_sub():
            a = random.randint(0, 100)
            b = random.randint(0, a)
            return a, '-', b

        def rand_mul():
            a = random.randint(0, 10)
            b = random.randint(0, 10)
            return a, '*', b

        def rand_div():
            b = random.randint(1, 10)
            res = random.randint(0, 10)
            a = res * b
            return a, '/', b

        op_funcs = []
        if '+' in ops:
            op_funcs.append(rand_sum)
        if '-' in ops:
            op_funcs.append(rand_sub)
        if '*' in ops:
            op_funcs.append(rand_mul)
        if '/' in ops:
            op_funcs.append(rand_div)

        # === НОВЫЕ ТИПЫ ПРИМЕРОВ ===
        choice = random.random()

        # 1. Скобки (старый тип) — ~30%
        if choice < 0.3 and op_funcs:
            left_func = random.choice(op_funcs)
            right_func = random.choice(op_funcs)
            if random.choice([True, False]):
                a, op1, b = left_func()
                c, op2, d = right_func()
                expr = f"({a} {op1} {b}) {op2} {d}"
            else:
                a, op1, b = left_func()
                c, op2, d = right_func()
                expr = f"{a} {op1} ({c} {op2} {d})"
            try:
                value = eval(expr.replace(' ', ''))
            except Exception:
                return self.generate_parentheses_example(allowed_ops)
            if isinstance(value, (int, float)) and value == int(value) and 0 <= int(value) <= 100:
                return {'type': 'parentheses', 'expr': expr}

        # 2. Формула: a * b + c / d (без скобок, но с приоритетом) — ~40%
        elif choice < 0.7:
            # Выбираем операции для левой и правой части
            left_op = random.choice(['*', '/'])
            right_op = random.choice(['+', '-'])

            # Генерируем левую часть (умножение/деление → целое)
            if left_op == '*':
                a = random.randint(0, 10)
                b = random.randint(0, 10)
                left_val = a * b
            else:  # '/'
                b = random.randint(1, 10)
                left_val = random.randint(0, 10)
                a = left_val * b

            # Генерируем правую часть (умножение/деление → целое)
            right_op_muldiv = random.choice(['*', '/'])
            if right_op_muldiv == '*':
                c = random.randint(0, 10)
                d = random.randint(0, 10)
                right_val = c * d
            else:  # '/'
                d = random.randint(1, 10)
                right_val = random.randint(0, 10)
                c = right_val * d

            # Собираем выражение: левая часть + (или -) правая часть
            if right_op == '+':
                total = left_val + right_val
                if 0 <= total <= 100:
                    expr = f"{a} {left_op} {b} {right_op} {c} {right_op_muldiv} {d}"
                    return {'type': 'complex_no_parentheses', 'expr': expr}
            else:  # '-'
                total = left_val - right_val
                if 0 <= total <= 100:
                    expr = f"{a} {left_op} {b} {right_op} {c} {right_op_muldiv} {d}"
                    return {'type': 'complex_no_parentheses', 'expr': expr}

        # 3. Формула: a * b / c (только * и /) — ~30%
        else:
            # Генерируем три числа и две операции (* или /)
            ops_list = [random.choice(['*', '/']) for _ in range(2)]
            # Первое число
            a = random.randint(0, 10)
            # Второе число
            if ops_list[0] == '*':
                b = random.randint(0, 10)
                temp = a * b
            else:  # '/'
                b = random.randint(1, 10)
                temp_val = random.randint(0, 10)
                a = temp_val * b
                temp = temp_val

            # Третье число
            if ops_list[1] == '*':
                c = random.randint(0, 10)
                final = temp * c
            else:  # '/'
                c = random.randint(1, 10)
                if temp % c != 0:
                    # Пропускаем, чтобы результат был целым
                    return self.generate_parentheses_example(allowed_ops)
                final = temp // c

            if 0 <= final <= 100:
                expr = f"{a} {ops_list[0]} {b} {ops_list[1]} {c}"
                return {'type': 'muldiv_chain', 'expr': expr}

        # Если не получилось — рекурсивно пробуем снова
        return self.generate_parentheses_example(allowed_ops)

    def solve_parentheses_example(self, expr_str, user_answer):
        try:
            correct = eval(expr_str.replace(' ', ''))
        except Exception:
            return False
        return int(user_answer) == correct

    def _rand(self, a, b):
        return random.randint(a, b)