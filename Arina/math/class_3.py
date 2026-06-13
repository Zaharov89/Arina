import random
from typing import Callable, Optional

from Arina.utils.safe_math import SafeMathExpressionError, safe_eval_math_expr


class MathExamplesClass3:
    def __init__(self, example_type, table_num):
        self.type = example_type
        self.table_num = table_num

    def generate_example(self):
        if self.type == "simple_equation":
            return self.generate_simple_equation()

        if self.type == "parentheses":
            return self.generate_parentheses_example()

        if self.type == "all":
            ops = ["+", "-", "*", "/"]
        elif self.type == "addsub":
            ops = ["+", "-"]
        elif self.type == "muldiv":
            ops = ["*", "/"]
        else:
            ops = [self.type]

        ops = [op for op in ops if op in ["+", "-", "*", "/"]]

        if not ops:
            ops = ["+", "-"]

        for _ in range(100):
            op = random.choice(ops)

            if op in ["*", "/"]:
                a = random.randint(0, 10)
                b = random.randint(1, 10)

                if op == "/":
                    result = random.randint(0, 10)
                    a = result * b
                    res = a // b
                else:
                    res = a * b

            else:
                if op == "+":
                    a = random.randint(0, 100)
                    b = random.randint(0, 100 - a)
                    res = a + b
                else:
                    a = random.randint(0, 100)
                    b = random.randint(0, a)
                    res = a - b

            if 0 <= res <= 100:
                return {"a": a, "op": op, "b": b}

        return {"a": 1, "op": "+", "b": 1}

    def calculate_answer(self, a, op, b):
        try:
            a = int(a)
            b = int(b)
        except (TypeError, ValueError):
            return None

        if op == "+":
            return a + b

        if op == "-":
            return a - b

        if op == "*":
            return a * b

        if op == "/":
            if b == 0:
                return None
            if a % b != 0:
                return None
            return a // b

        return None

    def generate_simple_equation(self, allowed_ops=None):
        ops = allowed_ops if allowed_ops else ["+", "-"]
        ops = [op for op in ops if op in ["+", "-"]]

        if not ops:
            ops = ["+"]

        for _ in range(100):
            op = random.choice(ops)

            if op == "+":
                x = random.randint(1, 50)
                b = random.randint(1, 50)
                result = x + b

                if result <= 100:
                    return {
                        "type": "simple_equation",
                        "question": f"x + {b} = {result}",
                        "x": x,
                    }

            else:
                result = random.randint(1, 50)
                x = random.randint(1, 50)
                a = result + x

                if a <= 100:
                    return {
                        "type": "simple_equation",
                        "question": f"{a} - x = {result}",
                        "x": x,
                    }

        return {
            "type": "simple_equation",
            "question": "x + 1 = 2",
            "x": 1,
        }

    def solve_simple_equation(self, expr_dict, user_x):
        try:
            return int(user_x) == int(expr_dict["x"])
        except (TypeError, ValueError, KeyError):
            return False

    def generate_parentheses_example(self, allowed_ops=None):
        ops = allowed_ops if allowed_ops else ["+", "-", "*", "/"]
        ops = [op for op in ops if op in ["+", "-", "*", "/"]]

        if not ops:
            ops = ["+", "-"]

        for _ in range(150):
            example = self._try_generate_parentheses_example(ops)

            if example is not None:
                return example

        return {"type": "fallback", "expr": "1 + 1"}

    def _try_generate_parentheses_example(self, ops: list[str]) -> Optional[dict]:
        generators = self._build_operation_generators(ops)

        if not generators:
            return None

        addsub_ops = [op for op in ops if op in ["+", "-"]]
        muldiv_ops = [op for op in ops if op in ["*", "/"]]

        available_modes = ["parentheses"]

        if addsub_ops and muldiv_ops:
            available_modes.append("complex_no_parentheses")

        if muldiv_ops:
            available_modes.append("muldiv_chain")

        mode = random.choice(available_modes)

        if mode == "parentheses":
            return self._generate_parentheses_mode(generators)

        if mode == "complex_no_parentheses":
            return self._generate_complex_no_parentheses_mode(addsub_ops, muldiv_ops)

        if mode == "muldiv_chain":
            return self._generate_muldiv_chain_mode(muldiv_ops)

        return None

    def _build_operation_generators(self, ops: list[str]) -> list[Callable[[], tuple[int, str, int]]]:
        generators = []

        if "+" in ops:
            generators.append(self._rand_sum)

        if "-" in ops:
            generators.append(self._rand_sub)

        if "*" in ops:
            generators.append(self._rand_mul)

        if "/" in ops:
            generators.append(self._rand_div)

        return generators

    def _generate_parentheses_mode(self, generators: list[Callable[[], tuple[int, str, int]]]) -> Optional[dict]:
        left_func = random.choice(generators)
        right_func = random.choice(generators)

        if random.choice([True, False]):
            a, op1, b = left_func()
            _, op2, d = right_func()
            expr = f"({a} {op1} {b}) {op2} {d}"
        else:
            a, op1, b = left_func()
            c, op2, d = right_func()
            expr = f"{a} {op1} ({c} {op2} {d})"

        return self._return_expr_if_valid("parentheses", expr)

    def _generate_complex_no_parentheses_mode(self, addsub_ops: list[str], muldiv_ops: list[str]) -> Optional[dict]:
        left_op = random.choice(muldiv_ops)
        right_op = random.choice(addsub_ops)
        right_op_muldiv = random.choice(muldiv_ops)

        if left_op == "*":
            a = random.randint(0, 10)
            b = random.randint(0, 10)
            left_val = a * b
        else:
            b = random.randint(1, 10)
            left_val = random.randint(0, 10)
            a = left_val * b

        if right_op_muldiv == "*":
            c = random.randint(0, 10)
            d = random.randint(0, 10)
            right_val = c * d
        else:
            d = random.randint(1, 10)
            right_val = random.randint(0, 10)
            c = right_val * d

        if right_op == "+":
            total = left_val + right_val
        else:
            total = left_val - right_val

        if 0 <= total <= 100:
            expr = f"{a} {left_op} {b} {right_op} {c} {right_op_muldiv} {d}"
            return self._return_expr_if_valid("complex_no_parentheses", expr)

        return None

    def _generate_muldiv_chain_mode(self, muldiv_ops: list[str]) -> Optional[dict]:
        ops_list = [random.choice(muldiv_ops) for _ in range(2)]

        a = random.randint(0, 10)

        if ops_list[0] == "*":
            b = random.randint(0, 10)
            temp = a * b
        else:
            b = random.randint(1, 10)
            temp_val = random.randint(0, 10)
            a = temp_val * b
            temp = temp_val

        if ops_list[1] == "*":
            c = random.randint(0, 10)
            final = temp * c
        else:
            c = random.randint(1, 10)

            if temp % c != 0:
                return None

            final = temp // c

        if 0 <= final <= 100:
            expr = f"{a} {ops_list[0]} {b} {ops_list[1]} {c}"
            return self._return_expr_if_valid("muldiv_chain", expr)

        return None

    def _return_expr_if_valid(self, example_type: str, expr: str) -> Optional[dict]:
        try:
            value = safe_eval_math_expr(expr)
        except SafeMathExpressionError:
            return None

        if 0 <= value <= 100:
            return {
                "type": example_type,
                "expr": expr,
            }

        return None

    def solve_parentheses_example(self, expr_str, user_answer):
        try:
            correct = safe_eval_math_expr(str(expr_str))
            return int(user_answer) == correct
        except (SafeMathExpressionError, TypeError, ValueError):
            return False

    def _rand_sum(self):
        a = random.randint(0, 100)
        b = random.randint(0, 100 - a)
        return a, "+", b

    def _rand_sub(self):
        a = random.randint(0, 100)
        b = random.randint(0, a)
        return a, "-", b

    def _rand_mul(self):
        a = random.randint(0, 10)
        b = random.randint(0, 10)
        return a, "*", b

    def _rand_div(self):
        b = random.randint(1, 10)
        result = random.randint(0, 10)
        a = result * b
        return a, "/", b

    def _rand(self, a, b):
        return random.randint(a, b)