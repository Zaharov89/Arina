import random
from typing import Callable, Any

from Arina.russian_language.class_1_topics import RUSSIAN_CLASS_1_TOPICS

MAX_UNIQUE_GENERATION_ATTEMPTS = 80
VOWELS = list("аоуыэяёюие")
CONSONANTS = list("бвгджзйклмнпрстфхцчшщ")


def get_topic_options_for_select() -> list[dict]:
    return [
        {"id": topic_id, "title": topic["title"], "short_title": topic.get("short_title", topic["title"])}
        for topic_id, topic in RUSSIAN_CLASS_1_TOPICS.items()
    ]


def normalize_text(value: Any) -> str:
    return str(value).strip().lower().replace("ё", "е")


def normalize_question_text(question: str) -> str:
    return normalize_text(question)


def make_choice_task(question: str, choices: list[str], correct: str, topic: str | None = None) -> dict:
    return {
        "question": question,
        "answer_type": "choice",
        "choices": choices,
        "correct": correct,
        "topic": topic,
    }


def make_text_task(question: str, correct: str, topic: str | None = None) -> dict:
    return {
        "question": question,
        "answer_type": "text",
        "correct": correct,
        "topic": topic,
    }


def make_number_task(question: str, correct: int, topic: str | None = None) -> dict:
    return {
        "question": question,
        "answer_type": "number",
        "correct": correct,
        "topic": topic,
    }


def generate_unique_task(generator: Callable[[], dict], used_questions: list[str] | None = None) -> dict:
    used_normalized = {normalize_question_text(question) for question in (used_questions or [])}
    fallback_task = None

    for _ in range(MAX_UNIQUE_GENERATION_ATTEMPTS):
        task = generator()
        fallback_task = task
        question = normalize_question_text(task.get("question", ""))

        if not question or question not in used_normalized:
            task["is_repeat"] = False
            return task

    if fallback_task is None:
        fallback_task = generator()
    fallback_task["is_repeat"] = True
    return fallback_task


def generate_russian_class_1_topic_task(topic_id: str, used_questions: list[str] | None = None) -> dict:
    generators = {
        "sounds_and_letters": generate_sounds_and_letters_task,
        "vowels": generate_vowels_task,
        "consonants": generate_consonants_task,
        "hard_soft_consonants": generate_hard_soft_consonants_task,
        "voiced_voiceless": generate_voiced_voiceless_task,
        "syllable": generate_syllable_task,
        "stress": generate_stress_task,
        "word": generate_word_task,
        "sentence": generate_sentence_task,
        "capital_letter": generate_capital_letter_task,
        "punctuation": generate_punctuation_task,
        "word_transfer": generate_word_transfer_task,
        "zhi_shi_cha_shcha_chu_shchu": generate_zhi_shi_task,
        "mini_dictations": generate_mini_dictation_task,
    }

    generator = generators.get(topic_id, generate_sounds_and_letters_task)
    task = generate_unique_task(generator, used_questions)
    task["topic"] = topic_id
    task["topic_title"] = RUSSIAN_CLASS_1_TOPICS.get(topic_id, {}).get("title", "Русский язык 1 класс")
    return task


def generate_sounds_and_letters_task() -> dict:
    tasks = [
        make_choice_task("Что мы слышим и произносим?", ["звук", "буква", "слово"], "звук", "sounds_and_letters"),
        make_choice_task("Что мы видим и пишем?", ["звук", "буква", "слог"], "буква", "sounds_and_letters"),
        make_choice_task("Из чего состоит написанное слово?", ["из букв", "из чисел", "из нот"], "из букв", "sounds_and_letters"),
        make_choice_task("Что произносим в слове “кот”: к-о-т?", ["звуки", "цифры", "предложения"], "звуки", "sounds_and_letters"),
    ]
    return random.choice(tasks)


def generate_vowels_task() -> dict:
    words = [
        ("кот", "о"),
        ("дом", "о"),
        ("мама", "а"),
        ("луна", "у"),
        ("лиса", "и"),
        ("сыр", "ы"),
    ]
    word, vowel = random.choice(words)
    tasks = [
        make_choice_task("Выбери гласную букву:", [random.choice(CONSONANTS), vowel, random.choice(CONSONANTS)], vowel, "vowels"),
        make_text_task(f"Какая гласная буква есть в слове “{word}”?", vowel, "vowels"),
        make_choice_task(f"Какая буква в слове “{word}” гласная?", list(dict.fromkeys(list(word))), vowel, "vowels"),
    ]
    return random.choice(tasks)


def generate_consonants_task() -> dict:
    words = [
        ("дом", "д"),
        ("кот", "к"),
        ("мама", "м"),
        ("лиса", "л"),
        ("сыр", "с"),
    ]
    word, consonant = random.choice(words)
    tasks = [
        make_choice_task("Выбери согласную букву:", [random.choice(VOWELS), consonant, random.choice(VOWELS)], consonant, "consonants"),
        make_text_task(f"Какая согласная буква стоит первой в слове “{word}”?", consonant, "consonants"),
        make_choice_task(f"Какая буква в слове “{word}” согласная?", list(dict.fromkeys(list(word))), consonant, "consonants"),
    ]
    return random.choice(tasks)


def generate_hard_soft_consonants_task() -> dict:
    tasks = [
        make_choice_task("В каком слове первый согласный мягкий?", ["лук", "люк"], "люк", "hard_soft_consonants"),
        make_choice_task("В каком слове звук Н мягкий?", ["кон", "конь"], "конь", "hard_soft_consonants"),
        make_choice_task("Что делает мягкий знак?", ["смягчает согласный", "обозначает гласный", "ставит ударение"], "смягчает согласный", "hard_soft_consonants"),
        make_choice_task("Какая буква часто показывает мягкость согласного?", ["и", "ы", "а"], "и", "hard_soft_consonants"),
    ]
    return random.choice(tasks)


def generate_voiced_voiceless_task() -> dict:
    tasks = [
        make_choice_task("Найди пару к букве Б:", ["п", "т", "с"], "п", "voiced_voiceless"),
        make_choice_task("Найди пару к букве Д:", ["т", "к", "ш"], "т", "voiced_voiceless"),
        make_choice_task("Какая буква звонкая?", ["б", "п"], "б", "voiced_voiceless"),
        make_choice_task("Какая буква глухая?", ["д", "т"], "т", "voiced_voiceless"),
        make_choice_task("Найди пару к букве З:", ["с", "ф", "к"], "с", "voiced_voiceless"),
    ]
    return random.choice(tasks)


def generate_syllable_task() -> dict:
    tasks = [
        make_number_task("Сколько слогов в слове “мама”?", 2, "syllable"),
        make_number_task("Сколько слогов в слове “кот”?", 1, "syllable"),
        make_number_task("Сколько слогов в слове “молоко”?", 3, "syllable"),
        make_choice_task("Выбери правильное деление слова “лиса” на слоги:", ["ли-са", "л-иса", "лис-а"], "ли-са", "syllable"),
        make_choice_task("Выбери правильное деление слова “мама” на слоги:", ["ма-ма", "м-ама", "мам-а"], "ма-ма", "syllable"),
    ]
    return random.choice(tasks)


def generate_stress_task() -> dict:
    tasks = [
        make_choice_task("Где ударение в слове “рука”?", ["ру", "ка"], "ка", "stress"),
        make_choice_task("Где ударение в слове “мама”?", ["ма первый", "ма второй"], "ма первый", "stress"),
        make_choice_task("Где ударение в слове “молоко”?", ["мо", "ло", "ко"], "ко", "stress"),
        make_choice_task("Какой слог произносится сильнее?", ["ударный", "безударный"], "ударный", "stress"),
    ]
    return random.choice(tasks)


def generate_word_task() -> dict:
    tasks = [
        make_choice_task("Какое слово называет предмет?", ["кот", "бежит", "белый"], "кот", "word"),
        make_choice_task("Какое слово называет действие?", ["дом", "идёт", "красный"], "идёт", "word"),
        make_choice_task("Какое слово называет признак?", ["мяч", "спит", "большой"], "большой", "word"),
        make_choice_task("Как пишутся слова в предложении?", ["отдельно", "слитно", "через запятую"], "отдельно", "word"),
    ]
    return random.choice(tasks)


def generate_sentence_task() -> dict:
    tasks = [
        make_choice_task("Выбери предложение:", ["Кот спит.", "кот", "весёлый"], "Кот спит.", "sentence"),
        make_choice_task("Какое предложение записано правильно?", ["кот спит.", "Кот спит."], "Кот спит.", "sentence"),
        make_choice_task("Составь предложение из слов “спит / Кот”:", ["Кот спит.", "спит Кот", "Кот"], "Кот спит.", "sentence"),
        make_choice_task("Что выражает предложение?", ["законченную мысль", "только букву", "только звук"], "законченную мысль", "sentence"),
    ]
    return random.choice(tasks)


def generate_capital_letter_task() -> dict:
    tasks = [
        make_choice_task("Как правильно написать имя?", ["маша", "Маша"], "Маша", "capital_letter"),
        make_choice_task("Как правильно начать предложение?", ["арина читает.", "Арина читает."], "Арина читает.", "capital_letter"),
        make_choice_task("Как правильно написать кличку животного?", ["барсик", "Барсик"], "Барсик", "capital_letter"),
        make_choice_task("Что пишется с большой буквы?", ["имя человека", "любой слог", "любая гласная"], "имя человека", "capital_letter"),
    ]
    return random.choice(tasks)


def generate_punctuation_task() -> dict:
    tasks = [
        make_choice_task("Какой знак нужен? Где мама__", [".", "?", "!"], "?", "punctuation"),
        make_choice_task("Какой знак нужен? Я иду домой__", [".", "?", "!"], ".", "punctuation"),
        make_choice_task("Какой знак нужен? Как красиво__", [".", "?", "!"], "!", "punctuation"),
        make_choice_task("Какой знак ставится в конце вопроса?", [".", "?", "!"], "?", "punctuation"),
    ]
    return random.choice(tasks)


def generate_word_transfer_task() -> dict:
    tasks = [
        make_choice_task("Можно ли перенести слово “мама”?", ["да", "нет"], "да", "word_transfer"),
        make_choice_task("Можно ли перенести слово “дом”?", ["да", "нет"], "нет", "word_transfer"),
        make_choice_task("Выбери правильный перенос:", ["ма-ма", "м-ама"], "ма-ма", "word_transfer"),
        make_choice_task("Можно ли оставлять одну букву на строке?", ["да", "нет"], "нет", "word_transfer"),
    ]
    return random.choice(tasks)


def generate_zhi_shi_task() -> dict:
    tasks = [
        make_choice_task("Выбери правильное написание:", ["жираф", "жыраф"], "жираф", "zhi_shi_cha_shcha_chu_shchu"),
        make_choice_task("Выбери правильное написание:", ["машина", "машына"], "машина", "zhi_shi_cha_shcha_chu_shchu"),
        make_choice_task("Выбери правильное написание:", ["часы", "чясы"], "часы", "zhi_shi_cha_shcha_chu_shchu"),
        make_choice_task("Выбери правильное написание:", ["щука", "щюка"], "щука", "zhi_shi_cha_shcha_chu_shchu"),
        make_choice_task("Как пишутся ЖИ и ШИ?", ["с И", "с Ы"], "с И", "zhi_shi_cha_shcha_chu_shchu"),
    ]
    return random.choice(tasks)


def generate_mini_dictation_task() -> dict:
    tasks = [
        make_text_task("Напиши слово: мама", "мама", "mini_dictations"),
        make_text_task("Напиши слово: кот", "кот", "mini_dictations"),
        make_text_task("Напиши слово: дом", "дом", "mini_dictations"),
        make_text_task("Напиши слово: лиса", "лиса", "mini_dictations"),
        make_text_task("Напиши предложение: Мама дома.", "Мама дома.", "mini_dictations"),
        make_text_task("Напиши предложение: Кот спит.", "Кот спит.", "mini_dictations"),
    ]
    return random.choice(tasks)
