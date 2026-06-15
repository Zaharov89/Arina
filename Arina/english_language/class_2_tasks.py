from Arina.russian_language.class_1_tasks import make_choice_task, generate_unique_task
from Arina.english_language.class_2_topics import ENGLISH_CLASS_2_TOPICS


def generate_english_class_2_topic_task(topic_id: str, used_questions: list[str] | None = None) -> dict:
    generators = {
        "alphabet_en": lambda: make_choice_task("Какая буква идёт после A?", ["B", "C", "D"], "B", topic_id),
        "sounds_reading": lambda: make_choice_task("Как переводится слово cat?", ["кот", "собака", "рыба"], "кот", topic_id),
        "greetings": lambda: make_choice_task("Как сказать “привет” по-английски?", ["Hello", "Bye", "Red"], "Hello", topic_id),
        "family_en": lambda: make_choice_task("Mother — это:", ["мама", "папа", "сестра"], "мама", topic_id),
        "colors_en": lambda: make_choice_task("Red — это:", ["красный", "синий", "зелёный"], "красный", topic_id),
        "numbers_1_10_en": lambda: make_choice_task("Five — это:", ["пять", "четыре", "семь"], "пять", topic_id),
        "school_items_en": lambda: make_choice_task("Book — это:", ["книга", "ручка", "стол"], "книга", topic_id),
        "toys_en": lambda: make_choice_task("Ball — это:", ["мяч", "кукла", "поезд"], "мяч", topic_id),
        "animals_en": lambda: make_choice_task("Dog — это:", ["собака", "кошка", "слон"], "собака", topic_id),
        "food_en": lambda: make_choice_task("Apple — это:", ["яблоко", "молоко", "сыр"], "яблоко", topic_id),
        "home_rooms_en": lambda: make_choice_task("Kitchen — это:", ["кухня", "сад", "дверь"], "кухня", topic_id),
        "simple_phrases_en": lambda: make_choice_task("Как переводится “I have a pen”?", ["У меня есть ручка", "Я красный", "Это дом"], "У меня есть ручка", topic_id),
        "vocabulary_words_en_2": lambda: make_choice_task("Sheep — это:", ["овца", "рыба", "сыр"], "овца", topic_id),
    }
    generator = generators.get(topic_id, generators["alphabet_en"])
    task = generate_unique_task(generator, used_questions)
    task["topic"] = topic_id
    task["topic_title"] = ENGLISH_CLASS_2_TOPICS.get(topic_id, {}).get("title", "Английский язык 2 класс")
    return task
