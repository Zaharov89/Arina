from flask import Blueprint, jsonify, request

from Arina.english_language.class_2 import class2Words
from Arina.english_language.class_3 import class3Words
from Arina.russian_language.class_2 import russianQuestions as questions2
from Arina.russian_language.class_3 import russianQuestions as questions3

vocabulary_api_bp = Blueprint("vocabulary_api", __name__)


@vocabulary_api_bp.route("/questions")
def questions():
    mode = request.args.get("mode", "all")

    if mode == "2":
        return jsonify(questions2)

    if mode == "3":
        return jsonify(questions3)

    if mode == "en_all":
        return jsonify(class2Words + class3Words)

    if mode == "en_2":
        return jsonify(class2Words)

    if mode == "en_3":
        return jsonify(class3Words)

    if mode == "all":
        all_questions = {**questions2, **questions3}
        return jsonify(all_questions)

    return jsonify({})
