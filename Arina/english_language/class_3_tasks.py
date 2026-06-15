from Arina.russian_language.class_1_tasks import make_choice_task, generate_unique_task
from Arina.english_language.class_3_topics import ENGLISH_CLASS_3_TOPICS


def generate_english_class_3_topic_task(topic_id: str, used_questions: list[str] | None = None) -> dict:
    generators = {
        "reading_rules_3": lambda: make_choice_task("Как переводится слово ship?", ["корабль", "овца", "магазин"], "корабль", topic_id),
        "personal_info_3": lambda: make_choice_task("Как сказать “Меня зовут Анна”?", ["My name is Ann", "I like Ann", "This is Ann"], "My name is Ann", topic_id),
        "family_friends_3": lambda: make_choice_task("Friend — это:", ["друг", "семья", "учитель"], "друг", topic_id),
        "numbers_1_100_en": lambda: make_choice_task("Thirty — это:", ["тридцать", "тринадцать", "три"], "тридцать", topic_id),
        "days_months_en": lambda: make_choice_task("Monday — это:", ["понедельник", "вторник", "январь"], "понедельник", topic_id),
        "school_subjects_en": lambda: make_choice_task("Maths — это:", ["математика", "музыка", "чтение"], "математика", topic_id),
        "daily_routine_en": lambda: make_choice_task("Get up — это:", ["вставать", "спать", "читать"], "вставать", topic_id),
        "food_likes_en": lambda: make_choice_task("Как перевести “I like apples”?", ["Мне нравятся яблоки", "У меня есть яблоки", "Я вижу яблоки"], "Мне нравятся яблоки", topic_id),
        "animals_3_en": lambda: make_choice_task("Tiger — это:", ["тигр", "кот", "собака"], "тигр", topic_id),
        "home_city_en": lambda: make_choice_task("City — это:", ["город", "дом", "улица"], "город", topic_id),
        "present_simple_intro": lambda: make_choice_task("Как правильно: He ___ football.", ["plays", "play", "playing"], "plays", topic_id),
        "questions_short_answers": lambda: make_choice_task("Краткий ответ на “Do you like milk?”:", ["Yes, I do", "Yes, I am", "Yes, I have"], "Yes, I do", topic_id),
        "vocabulary_words_en_3": lambda: make_choice_task("Holiday — это:", ["праздник", "дом", "урок"], "праздник", topic_id),
    }
    generator = generators.get(topic_id, generators["reading_rules_3"])
    task = generate_unique_task(generator, used_questions)
    task["topic"] = topic_id
    task["topic_title"] = ENGLISH_CLASS_3_TOPICS.get(topic_id, {}).get("title", "Английский язык 3 класс")
    return task
