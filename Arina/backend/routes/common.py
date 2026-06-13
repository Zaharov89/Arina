from typing import Any, Dict, Optional, Tuple

from flask import jsonify, request

from Arina.config import DEFAULT_STUDENT


def get_student() -> str:
    student = request.args.get("student", DEFAULT_STUDENT)
    return student.strip() or DEFAULT_STUDENT


def get_int_arg(name: str, default: int, min_value: int, max_value: int) -> int:
    raw_value = request.args.get(name, default)

    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return default

    return max(min_value, min(value, max_value))


def get_json_body() -> Tuple[Optional[Dict[str, Any]], Optional[Tuple[Any, int]]]:
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None, (jsonify({"error": "JSON body is required"}), 400)

    return data, None
