import pytest

from Arina.utils.safe_math import SafeMathExpressionError, safe_eval_math_expr


def test_safe_eval_respects_operator_priority():
    assert safe_eval_math_expr("2 + 2 * 2") == 6


def test_safe_eval_parentheses_and_integer_division():
    assert safe_eval_math_expr("(10 - 4) / 2") == 3


def test_safe_eval_rejects_code_execution():
    with pytest.raises(SafeMathExpressionError):
        safe_eval_math_expr("__import__('os').system('echo hacked')")


def test_safe_eval_rejects_division_by_zero():
    with pytest.raises(SafeMathExpressionError):
        safe_eval_math_expr("10 / 0")
