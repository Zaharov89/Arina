import ast
import operator as op
import re
from typing import Union


Number = Union[int, float]


class SafeMathExpressionError(ValueError):
    """Ошибка безопасного вычисления математического выражения."""


_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

_ALLOWED_CHARS_RE = re.compile(r"^[0-9+\-*/().\s]+$")


def safe_eval_math_expr(expr: str) -> int:
    """
    Безопасно вычисляет простые арифметические выражения.

    Разрешены только:
    - числа;
    - +, -, *, /, //;
    - скобки;
    - пробелы.

    Запрещены:
    - имена переменных;
    - вызовы функций;
    - импорты;
    - атрибуты;
    - любые Python-конструкции кроме арифметики.

    Возвращает int.
    Если результат деления не целый — выбрасывает SafeMathExpressionError.
    """
    if not isinstance(expr, str):
        raise SafeMathExpressionError("Expression must be a string")

    normalized_expr = expr.strip()

    if not normalized_expr:
        raise SafeMathExpressionError("Expression is empty")

    if len(normalized_expr) > 100:
        raise SafeMathExpressionError("Expression is too long")

    if not _ALLOWED_CHARS_RE.fullmatch(normalized_expr):
        raise SafeMathExpressionError("Expression contains forbidden characters")

    try:
        tree = ast.parse(normalized_expr, mode="eval")
    except SyntaxError as exc:
        raise SafeMathExpressionError("Invalid expression syntax") from exc

    result = _eval_node(tree)

    if isinstance(result, float):
        if not result.is_integer():
            raise SafeMathExpressionError("Expression result is not integer")
        result = int(result)

    return int(result)


def _eval_node(node: ast.AST) -> Number:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            raise SafeMathExpressionError("Boolean values are forbidden")
        if isinstance(node.value, (int, float)):
            return node.value
        raise SafeMathExpressionError("Only numbers are allowed")

    # Для совместимости со старыми версиями Python
    if isinstance(node, ast.Num):
        return node.n

    if isinstance(node, ast.BinOp):
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise SafeMathExpressionError("Operator is not allowed")

        left = _eval_node(node.left)
        right = _eval_node(node.right)

        if operator_type in (ast.Div, ast.FloorDiv) and right == 0:
            raise SafeMathExpressionError("Division by zero")

        result = _ALLOWED_OPERATORS[operator_type](left, right)

        if isinstance(result, float) and not result.is_integer():
            raise SafeMathExpressionError("Division result is not integer")

        return int(result)

    if isinstance(node, ast.UnaryOp):
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise SafeMathExpressionError("Unary operator is not allowed")

        operand = _eval_node(node.operand)
        return _ALLOWED_OPERATORS[operator_type](operand)

    raise SafeMathExpressionError("Unsupported expression")