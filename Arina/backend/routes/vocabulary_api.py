from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from Arina.database.session import get_session_factory
from Arina.english_language.vocabulary import get_english_vocabulary_words
from Arina.russian_language.vocabulary import get_russian_vocabulary_map, get_russian_vocabulary_words

vocabulary_api_bp = Blueprint("vocabulary_api", __name__)


def parse_class_number(raw_value: str | None, allowed: set[int]) -> int | None:
    if not raw_value:
        return None
    try:
        class_number = int(raw_value)
    except ValueError:
        return None
    return class_number if class_number in allowed else None


@vocabulary_api_bp.route("/api/russian/vocabulary")
def russian_vocabulary_api():
    class_number = parse_class_number(request.args.get("class_number"), {1, 2, 3})
    if request.args.get("class_number") and class_number is None:
        return jsonify({"status": "validation_error", "message": "class_number должен быть 1, 2 или 3."}), 400

    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            words = get_russian_vocabulary_words(session, class_number)
        return jsonify({"status": "ok", "data": words})
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify({"status": "error", "message": "Не удалось получить словарные слова русского языка.", "error": str(error)}), 500


@vocabulary_api_bp.route("/api/english/vocabulary")
def english_vocabulary_api():
    class_number = parse_class_number(request.args.get("class_number"), {2, 3})
    if request.args.get("class_number") and class_number is None:
        return jsonify({"status": "validation_error", "message": "class_number должен быть 2 или 3."}), 400

    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            words = get_english_vocabulary_words(session, class_number)
        return jsonify({"status": "ok", "data": words})
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify({"status": "error", "message": "Не удалось получить английские слова из БД.", "error": str(error)}), 500


@vocabulary_api_bp.route("/questions")
def questions():
    mode = request.args.get("mode", "all")

    if mode in {"1", "2", "3", "all"}:
        class_number = None if mode == "all" else int(mode)
        try:
            session_factory = get_session_factory()
            with session_factory() as session:
                return jsonify(get_russian_vocabulary_map(session, class_number))
        except (RuntimeError, SQLAlchemyError, OSError):
            return jsonify({})

    if mode in {"en_all", "en_2", "en_3"}:
        class_number = None if mode == "en_all" else int(mode[-1])
        try:
            session_factory = get_session_factory()
            with session_factory() as session:
                return jsonify(get_english_vocabulary_words(session, class_number))
        except (RuntimeError, SQLAlchemyError, OSError):
            return jsonify([])

    return jsonify({})
