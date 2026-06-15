import random

from Arina.russian_language.class_1_tasks import make_choice_task, generate_unique_task
from Arina.english_language.class_3_topics import ENGLISH_CLASS_3_TOPICS


TASK_DATA = {
    "reading_rules_3": [("Как переводится слово ship?", ["корабль", "овца", "магазин"], "корабль"), ("Chair — это:", ["стул", "кошка", "ручка"], "стул"), ("Phone — это:", ["телефон", "дом", "сыр"], "телефон")],
    "personal_info_3": [("Как сказать “Меня зовут Анна”?", ["My name is Ann", "I like Ann", "This is Ann"], "My name is Ann"), ("Как сказать “Мне 9 лет”?", ["I am nine", "I have nine", "I see nine"], "I am nine"), ("I live in Moscow — это:", ["Я живу в Москве", "Я люблю Москву", "Это Москва"], "Я живу в Москве")],
    "family_friends_3": [("Friend — это:", ["друг", "семья", "учитель"], "друг"), ("Parents — это:", ["родители", "друзья", "дети"], "родители"), ("Brother — это:", ["брат", "сестра", "папа"], "брат")],
    "numbers_1_100_en": [("Thirty — это:", ["тридцать", "тринадцать", "три"], "тридцать"), ("Forty — это:", ["сорок", "четырнадцать", "четыре"], "сорок"), ("One hundred — это:", ["сто", "десять", "один"], "сто")],
    "days_months_en": [("Monday — это:", ["понедельник", "вторник", "январь"], "понедельник"), ("Friday — это:", ["пятница", "среда", "май"], "пятница"), ("January — это:", ["январь", "понедельник", "июнь"], "январь")],
    "school_subjects_en": [("Maths — это:", ["математика", "музыка", "чтение"], "математика"), ("English — это:", ["английский", "рисование", "спорт"], "английский"), ("Music — это:", ["музыка", "математика", "окно"], "музыка")],
    "daily_routine_en": [("Get up — это:", ["вставать", "спать", "читать"], "вставать"), ("Go to school — это:", ["идти в школу", "играть", "обедать"], "идти в школу"), ("Have breakfast — это:", ["завтракать", "спать", "бегать"], "завтракать")],
    "food_likes_en": [("Как перевести “I like apples”?", ["Мне нравятся яблоки", "У меня есть яблоки", "Я вижу яблоки"], "Мне нравятся яблоки"), ("I don't like milk — это:", ["Мне не нравится молоко", "Я пью молоко", "Это молоко"], "Мне не нравится молоко"), ("I like bread — это:", ["Мне нравится хлеб", "Я вижу хлеб", "У меня хлеб"], "Мне нравится хлеб")],
    "animals_3_en": [("Tiger — это:", ["тигр", "кот", "собака"], "тигр"), ("Lion — это:", ["лев", "лиса", "рыба"], "лев"), ("Elephant — это:", ["слон", "тигр", "мышь"], "слон")],
    "home_city_en": [("City — это:", ["город", "дом", "улица"], "город"), ("Street — это:", ["улица", "комната", "сад"], "улица"), ("Flat — это:", ["квартира", "площадь", "школа"], "квартира")],
    "present_simple_intro": [("Как правильно: He ___ football.", ["plays", "play", "playing"], "plays"), ("Как правильно: I ___ apples.", ["like", "likes", "liking"], "like"), ("Как правильно: She ___ milk.", ["likes", "like", "liking"], "likes")],
    "questions_short_answers": [("Краткий ответ на “Do you like milk?”:", ["Yes, I do", "Yes, I am", "Yes, I have"], "Yes, I do"), ("Краткий отрицательный ответ на “Do you like tea?”:", ["No, I don't", "No, I am", "No, I have"], "No, I don't"), ("Вопрос начинается правильно:", ["Do you like cats?", "You do like cats?", "Like you cats?"], "Do you like cats?")],
    "vocabulary_words_en_3": [("Holiday — это:", ["праздник", "дом", "урок"], "праздник"), ("Together — это:", ["вместе", "быстро", "завтра"], "вместе"), ("Weather — это:", ["погода", "еда", "улица"], "погода")],
}


def generate_english_class_3_topic_task(topic_id: str, used_questions: list[str] | None = None) -> dict:
    tasks = TASK_DATA.get(topic_id, TASK_DATA["reading_rules_3"])
    task = generate_unique_task(lambda: make_choice_task(*random.choice(tasks), topic_id), used_questions)
    task["topic"] = topic_id
    task["topic_title"] = ENGLISH_CLASS_3_TOPICS.get(topic_id, {}).get("title", "Английский язык 3 класс")
    return task
