import random
from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request
from sqlalchemy.exc import SQLAlchemyError

from Arina.backend.routes.common import get_int_arg, get_json_body, get_student
from Arina.backend.services.catalog import get_topic_or_none, merge_db_topics_with_content
from Arina.database.session import get_session_factory
from Arina.english_language.class_2_tasks import generate_english_class_2_topic_task
from Arina.english_language.class_2_topics import ENGLISH_CLASS_2_TOPICS
from Arina.english_language.class_3_tasks import generate_english_class_3_topic_task
from Arina.english_language.class_3_topics import ENGLISH_CLASS_3_TOPICS
from Arina.english_language.vocabulary import get_english_vocabulary_words
from Arina.russian_language.class_1_tasks import normalize_text

english_bp = Blueprint("english", __name__)

SUPPORTED_ENGLISH_CLASSES = list(range(1, 12))
IMPLEMENTED_TEST_CLASSES = {2, 3}
IMPLEMENTED_LEARNING_CLASSES = {2, 3}
CONTROL_SLICE_TYPE = "control_slice"
VOCABULARY_TOPIC_CODES = {"vocabulary_words_en_2", "vocabulary_words_en_3"}
control_topic_cursor = 0
TOPICS_BY_CLASS = {2: ENGLISH_CLASS_2_TOPICS, 3: ENGLISH_CLASS_3_TOPICS}
DEFAULT_TOPIC_BY_CLASS = {2: "alphabet_en", 3: "reading_rules_3"}

ENGLISH_TOPIC_WORDS = {
    "alphabet_en": [("A a", "эй", ""), ("B b", "би", ""), ("C c", "си", ""), ("D d", "ди", "")],
    "sounds_reading": [("cat", "кот", ""), ("dog", "собака", ""), ("fish", "рыба", "")],
    "greetings": [("Hello", "Привет", ""), ("Good morning", "Доброе утро", ""), ("Bye", "Пока", "")],
    "family_en": [("mother", "мама", ""), ("father", "папа", ""), ("sister", "сестра", ""), ("brother", "брат", "")],
    "colors_en": [("red", "красный", ""), ("blue", "синий", ""), ("green", "зелёный", ""), ("yellow", "жёлтый", "")],
    "numbers_1_10_en": [("one", "один", ""), ("two", "два", ""), ("five", "пять", ""), ("ten", "десять", "")],
    "school_items_en": [("book", "книга", ""), ("pen", "ручка", ""), ("pencil", "карандаш", ""), ("bag", "сумка", "")],
    "toys_en": [("ball", "мяч", ""), ("doll", "кукла", ""), ("car", "машина", "")],
    "animals_en": [("dog", "собака", ""), ("cat", "кошка", ""), ("bird", "птица", "")],
    "food_en": [("apple", "яблоко", ""), ("milk", "молоко", ""), ("bread", "хлеб", "")],
    "home_rooms_en": [("house", "дом", ""), ("room", "комната", ""), ("kitchen", "кухня", "")],
    "simple_phrases_en": [("I have a pen", "У меня есть ручка", ""), ("I like cats", "Мне нравятся кошки", "")],
    "vocabulary_words_en_2": [("sheep", "овца", ""), ("mouse", "мышь", ""), ("cheese", "сыр", "")],
    "reading_rules_3": [("ship", "корабль", ""), ("chair", "стул", ""), ("phone", "телефон", "")],
    "personal_info_3": [("My name is Ann", "Меня зовут Анна", ""), ("I am nine", "Мне девять", "")],
    "family_friends_3": [("friend", "друг", ""), ("parents", "родители", ""), ("brother", "брат", "")],
    "numbers_1_100_en": [("thirty", "тридцать", ""), ("forty", "сорок", ""), ("one hundred", "сто", "")],
    "days_months_en": [("Monday", "понедельник", ""), ("Friday", "пятница", ""), ("January", "январь", "")],
    "school_subjects_en": [("Maths", "математика", ""), ("English", "английский", ""), ("Music", "музыка", "")],
    "daily_routine_en": [("get up", "вставать", ""), ("go to school", "идти в школу", ""), ("have breakfast", "завтракать", "")],
    "food_likes_en": [("I like apples", "Мне нравятся яблоки", ""), ("I don't like milk", "Мне не нравится молоко", "")],
    "animals_3_en": [("tiger", "тигр", ""), ("lion", "лев", ""), ("elephant", "слон", "")],
    "home_city_en": [("city", "город", ""), ("street", "улица", ""), ("flat", "квартира", "")],
    "present_simple_intro": [("he plays", "он играет", ""), ("I like", "мне нравится", ""), ("she likes", "ей нравится", "")],
    "questions_short_answers": [("Yes, I do", "Да", ""), ("No, I don't", "Нет", ""), ("Do you like cats?", "Ты любишь кошек?", "")],
    "vocabulary_words_en_3": [("holiday", "праздник", ""), ("together", "вместе", ""), ("weather", "погода", "")],
}


def topic_words(topic_id: str) -> list[dict]:
    return [{"english_word": en, "russian_translation": ru, "transcription": tr} for en, ru, tr in ENGLISH_TOPIC_WORDS.get(topic_id, [])]


def get_english_words_for_class(class_num: str) -> list[dict]:
    class_number = None if class_num == "all" else int(class_num)
    session_factory = get_session_factory()
    with session_factory() as session:
        return get_english_vocabulary_words(session, class_number)


def get_english_class_words() -> tuple[list[dict], list[dict]]:
    return get_english_words_for_class("2"), get_english_words_for_class("3")


def get_english_topics(class_num: int) -> dict:
    return merge_db_topics_with_content("english", class_num, TOPICS_BY_CLASS.get(class_num, ENGLISH_CLASS_2_TOPICS))


def get_english_topic(class_num: int, topic_id: str) -> dict | None:
    return get_topic_or_none("english", class_num, topic_id, TOPICS_BY_CLASS.get(class_num, ENGLISH_CLASS_2_TOPICS))


def normalize_used_questions(raw_used_questions: Any) -> list[str]:
    if not isinstance(raw_used_questions, list):
        return []
    return [str(question).strip() for question in raw_used_questions if str(question).strip()][-300:]


def get_next_control_topic_id(class_num: int) -> str:
    global control_topic_cursor
    topic_ids = [topic_id for topic_id in get_english_topics(class_num).keys() if topic_id not in VOCABULARY_TOPIC_CODES]
    if not topic_ids:
        return DEFAULT_TOPIC_BY_CLASS.get(class_num, "alphabet_en")
    topic_id = topic_ids[control_topic_cursor % len(topic_ids)]
    control_topic_cursor += 1
    return topic_id


@english_bp.route("/english/menu")
def english_menu():
    return render_template("english/menu.html", classes=SUPPORTED_ENGLISH_CLASSES, implemented_test_classes=IMPLEMENTED_TEST_CLASSES, implemented_learning_classes=IMPLEMENTED_LEARNING_CLASSES, student=get_student())


@english_bp.route("/english/class/<int:class_num>")
def english_class_page(class_num: int):
    if class_num not in SUPPORTED_ENGLISH_CLASSES:
        abort(404)
    if class_num in IMPLEMENTED_LEARNING_CLASSES:
        return render_template("english/learning.html", student=get_student(), class_num=class_num, topics=get_english_topics(class_num), vocabulary_topic_codes=VOCABULARY_TOPIC_CODES)
    return render_template("english/class_page.html", student=get_student(), class_num=class_num, is_first_class=class_num == 1, is_testing_implemented=class_num in IMPLEMENTED_TEST_CLASSES)


@english_bp.route("/english/learning")
def english_learning():
    class_num = get_int_arg("class", default=2, min_value=1, max_value=11)
    if class_num not in IMPLEMENTED_LEARNING_CLASSES:
        return english_class_page(class_num)
    return render_template("english/learning.html", student=get_student(), class_num=class_num, topics=get_english_topics(class_num), vocabulary_topic_codes=VOCABULARY_TOPIC_CODES)


@english_bp.route("/english/learning/topic/<topic_id>")
def english_learning_topic(topic_id: str):
    class_num = get_int_arg("class", default=2, min_value=1, max_value=11)
    if topic_id in VOCABULARY_TOPIC_CODES:
        return render_template("english/vocabulary_menu.html", student=get_student(), class_num=class_num)
    topic = get_english_topic(class_num, topic_id)
    if not topic:
        abort(404)
    return render_template("english/learning_topic.html", student=get_student(), class_num=class_num, topic_id=topic_id, topic=topic, topic_words=topic_words(topic_id))


@english_bp.route("/english/learning/topic/<topic_id>/details")
def english_learning_topic_details(topic_id: str):
    class_num = get_int_arg("class", default=2, min_value=1, max_value=11)
    topic = get_english_topic(class_num, topic_id)
    if not topic:
        abort(404)
    return render_template("english/learning_detail.html", student=get_student(), class_num=class_num, topic_id=topic_id, topic=topic, topic_words=topic_words(topic_id))


@english_bp.route("/english/vocabulary-menu")
def english_vocabulary_menu():
    class_num = get_int_arg("class", default=2, min_value=2, max_value=3)
    return render_template("english/vocabulary_menu.html", student=get_student(), class_num=class_num)


@english_bp.route("/english/vocabulary-list")
def english_vocabulary_list():
    class_num = get_int_arg("class", default=2, min_value=2, max_value=3)
    try:
        words = get_english_words_for_class(str(class_num))
        error_message = None
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        words = []
        error_message = f"Не удалось получить английский словарь из БД: {error}"
    return render_template("english/vocabulary_list.html", student=get_student(), class_num=class_num, words=words, error_message=error_message)


@english_bp.route("/english/topic-test")
def english_topic_test():
    class_num = get_int_arg("class", default=2, min_value=1, max_value=11)
    topic_id = request.args.get("type", DEFAULT_TOPIC_BY_CLASS.get(class_num, "alphabet_en"))
    total_questions = get_int_arg("questions", default=25, min_value=1, max_value=50)
    if topic_id == CONTROL_SLICE_TYPE:
        total_questions = 50
    return render_template("english/topic_test.html", student=get_student(), class_num=class_num, test_settings={"classNum": str(class_num), "topicId": topic_id}, total_questions=total_questions, is_control_slice=topic_id == CONTROL_SLICE_TYPE)


@english_bp.route("/english/generate_task", methods=["POST"])
def generate_english_task():
    data, error_response = get_json_body()
    if error_response:
        return error_response
    class_num = int(data.get("class") or 2)
    topic_id = str(data.get("topic") or DEFAULT_TOPIC_BY_CLASS.get(class_num, "alphabet_en")).strip()
    if topic_id == CONTROL_SLICE_TYPE:
        topic_id = get_next_control_topic_id(class_num)
    if class_num == 3:
        task = generate_english_class_3_topic_task(topic_id, normalize_used_questions(data.get("used_questions")))
    else:
        task = generate_english_class_2_topic_task(topic_id, normalize_used_questions(data.get("used_questions")))
    return jsonify(task)


@english_bp.route("/english/check_task", methods=["POST"])
def check_english_task():
    data, error_response = get_json_body()
    if error_response:
        return error_response
    user_answer = data.get("answer", "")
    correct_answer = data.get("correct")
    if correct_answer is None:
        return jsonify({"result": "error", "message": "Не передан правильный ответ"}), 400
    if str(user_answer).strip() == "":
        return jsonify({"result": "empty", "correct_answer": correct_answer})
    return jsonify({"result": "correct" if normalize_text(user_answer) == normalize_text(correct_answer) else "incorrect", "correct_answer": correct_answer})


@english_bp.route("/english/vocabulary")
def english_vocabulary():
    return english_vocabulary_list()


@english_bp.route("/english/rules")
def english_rules():
    return english_learning()


@english_bp.route("/english/test_setup")
def english_test_setup():
    student = get_student()
    try:
        class2_words, class3_words = get_english_class_words()
        error_message = None
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        class2_words, class3_words = [], []
        error_message = f"Не удалось получить английский словарь из БД: {error}"
    return render_template("english/test_setup.html", class2_words=class2_words, class3_words=class3_words, student=student, error_message=error_message)


@english_bp.route("/english/test")
def english_test():
    student = get_student()
    class_num = request.args.get("class", "all")
    test_type = request.args.get("type", "en_to_ru")
    total_requested = get_int_arg("words", default=25, min_value=1, max_value=200)
    if class_num not in {"2", "3", "all"}:
        class_num = "all"
    try:
        all_available = get_english_words_for_class(class_num)
        class2_words, class3_words = get_english_class_words()
        error_message = None
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        all_available = []
        class2_words, class3_words = [], []
        error_message = f"Не удалось получить английский словарь из БД: {error}"
    if not all_available:
        test_words = []
    elif len(all_available) >= total_requested:
        test_words = random.sample(all_available, total_requested)
    else:
        test_words = random.choices(all_available, k=total_requested)
    return render_template("english/test.html", class2_words=class2_words, class3_words=class3_words, test_words=test_words, total_words=total_requested, test_type=test_type, student=student, error_message=error_message)
