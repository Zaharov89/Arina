import random
from typing import Any

from Arina.russian_language.class_1_tasks import make_choice_task, make_text_task, make_number_task, normalize_text, generate_unique_task
from Arina.russian_language.class_2_topics import RUSSIAN_CLASS_2_TOPICS


def generate_russian_class_2_topic_task(topic_id: str, used_questions: list[str] | None = None) -> dict:
    generators = {
        "sounds_letters_review": lambda: make_number_task("Сколько букв в слове “школа”?", 5, topic_id),
        "alphabet": lambda: make_choice_task("Какая буква идёт после Б?", ["А", "В", "Г"], "В", topic_id),
        "vowels_consonants": lambda: make_choice_task("Выбери гласную букву:", ["м", "о", "т"], "о", topic_id),
        "unstressed_vowels": lambda: make_choice_task("В каком слове есть безударная гласная?", ["трава", "дом", "мяч"], "трава", topic_id),
        "checked_unstressed_root": lambda: make_choice_task("Проверочное слово к слову “леса”:", ["лес", "лиса", "лесной"], "лес", topic_id),
        "paired_consonants": lambda: make_choice_task("Проверочное слово к слову “гриб”:", ["грибы", "грибок", "грибной"], "грибы", topic_id),
        "silent_consonants": lambda: make_choice_task("Где есть непроизносимая согласная?", ["солнце", "лиса", "дом"], "солнце", topic_id),
        "separating_soft_sign": lambda: make_choice_task("В каком слове есть разделительный мягкий знак?", ["семья", "конь", "мел"], "семья", topic_id),
        "noun": lambda: make_choice_task("Какое слово — имя существительное?", ["бежит", "зелёный", "книга"], "книга", topic_id),
        "adjective": lambda: make_choice_task("Какое слово — имя прилагательное?", ["красивый", "пишет", "ручка"], "красивый", topic_id),
        "verb": lambda: make_choice_task("Какое слово — глагол?", ["читает", "синий", "окно"], "читает", topic_id),
        "sentence_members": lambda: make_choice_task("В предложении “Мальчик рисует.” сказуемое:", ["мальчик", "рисует", "предложение"], "рисует", topic_id),
        "text_theme": lambda: make_choice_task("Если текст рассказывает о зиме, его тема:", ["зима", "лето", "школа"], "зима", topic_id),
        "vocabulary_words_2": lambda: make_text_task("Вставь словарное слово: __ — первый осенний месяц.", "сентябрь", topic_id),
    }
    generator = generators.get(topic_id, generators["sounds_letters_review"])
    task = generate_unique_task(generator, used_questions)
    task["topic"] = topic_id
    task["topic_title"] = RUSSIAN_CLASS_2_TOPICS.get(topic_id, {}).get("title", "Русский язык 2 класс")
    return task
