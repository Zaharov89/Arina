import logging

from flask import Blueprint, jsonify, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from Arina.auth.services import AuthTokenError
from Arina.backend.routes.common import get_int_arg, get_student
from Arina.typing_trainer.levels import ANIMALS, HAND_POSITIONS, LAYOUT_TITLES, get_level, get_layout_levels
from Arina.typing_trainer.services import TypingTrainerValidationError, get_progress, save_animal, save_attempt

logger = logging.getLogger(__name__)
typing_trainer_bp = Blueprint("typing_trainer", __name__)


def get_access_token_from_request() -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return ""


@typing_trainer_bp.route("/typing-trainer")
def typing_trainer_index():
    return render_template("typing_trainer/index.html", student=get_student())


@typing_trainer_bp.route("/typing-trainer/layout")
def typing_trainer_layout():
    return render_template("typing_trainer/layout_select.html", student=get_student(), layouts=LAYOUT_TITLES)


@typing_trainer_bp.route("/typing-trainer/animal")
def typing_trainer_animal():
    layout_code = request.args.get("layout", "ru")
    return render_template("typing_trainer/animal_select.html", student=get_student(), layout_code=layout_code, animals=ANIMALS)


@typing_trainer_bp.route("/typing-trainer/hand-position")
def typing_trainer_hand_position():
    layout_code = request.args.get("layout", "ru")
    animal_code = request.args.get("animal", "dino")
    hand_position = HAND_POSITIONS.get(layout_code, HAND_POSITIONS["ru"])
    return render_template("typing_trainer/hand_position.html", student=get_student(), layout_code=layout_code, animal_code=animal_code, hand_position=hand_position, layout_title=LAYOUT_TITLES.get(layout_code, "Русская раскладка"), animal=ANIMALS.get(animal_code, ANIMALS["dino"]))


@typing_trainer_bp.route("/typing-trainer/game")
def typing_trainer_game():
    layout_code = request.args.get("layout", "ru")
    animal_code = request.args.get("animal", "dino")
    level_number = get_int_arg("level", default=1, min_value=1, max_value=100)
    level = get_level(layout_code, level_number)
    return render_template("typing_trainer/game.html", student=get_student(), layout_code=layout_code, animal_code=animal_code, level=level, levels=get_layout_levels(layout_code), animal=ANIMALS.get(animal_code, ANIMALS["dino"]), layout_title=LAYOUT_TITLES.get(layout_code, "Русская раскладка"))


@typing_trainer_bp.route("/api/typing-trainer/progress")
def api_typing_trainer_progress():
    try:
        layout_code = request.args.get("layout", "ru")
        return jsonify(get_progress(get_access_token_from_request(), layout_code))
    except AuthTokenError as error:
        return jsonify({"status": "unauthorized", "message": str(error)}), 401
    except (TypingTrainerValidationError, ValueError) as error:
        return jsonify({"status": "validation_error", "message": str(error)}), 400
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        logger.exception("Typing trainer progress failed")
        return jsonify({"status": "error", "message": f"Не удалось получить прогресс тренажёра: {error}"}), 500


@typing_trainer_bp.route("/api/typing-trainer/animal", methods=["POST"])
def api_typing_trainer_animal():
    try:
        payload = request.get_json(silent=True) or {}
        return jsonify(save_animal(get_access_token_from_request(), payload.get("layout_code"), payload.get("animal_code")))
    except AuthTokenError as error:
        return jsonify({"status": "unauthorized", "message": str(error)}), 401
    except (TypingTrainerValidationError, ValueError) as error:
        return jsonify({"status": "validation_error", "message": str(error)}), 400
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        logger.exception("Typing trainer animal save failed")
        return jsonify({"status": "error", "message": f"Не удалось сохранить персонажа: {error}"}), 500


@typing_trainer_bp.route("/api/typing-trainer/attempts", methods=["POST"])
def api_typing_trainer_attempts():
    try:
        return jsonify(save_attempt(get_access_token_from_request(), request.get_json(silent=True) or {}))
    except AuthTokenError as error:
        return jsonify({"status": "unauthorized", "message": str(error)}), 401
    except (TypingTrainerValidationError, ValueError) as error:
        return jsonify({"status": "validation_error", "message": str(error)}), 400
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        logger.exception("Typing trainer attempt save failed")
        return jsonify({"status": "error", "message": f"Не удалось сохранить результат уровня: {error}"}), 500
