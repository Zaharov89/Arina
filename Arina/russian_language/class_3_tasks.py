from Arina.russian_language.class_1_tasks import make_choice_task, make_text_task, generate_unique_task
from Arina.russian_language.class_3_topics import RUSSIAN_CLASS_3_TOPICS


def generate_russian_class_3_topic_task(topic_id: str, used_questions: list[str] | None = None) -> dict:
    generators = {
        "word_structure": lambda: make_choice_task("Какая часть слова общая у родственных слов?", ["корень", "предлог", "точка"], "корень", topic_id),
        "root_prefix_suffix": lambda: make_choice_task("Что стоит перед корнем?", ["приставка", "суффикс", "окончание"], "приставка", topic_id),
        "spelling_prefixes": lambda: make_choice_task("Как пишется приставка со словом?", ["слитно", "отдельно", "через дефис"], "слитно", topic_id),
        "checked_vowels_3": lambda: make_choice_task("Проверочное слово к слову “поля”:", ["поле", "пыль", "полка"], "поле", topic_id),
        "paired_consonants_3": lambda: make_choice_task("Проверочное слово к слову “дуб”:", ["дубы", "дубок", "дубовый"], "дубы", topic_id),
        "parts_of_speech_3": lambda: make_choice_task("Какое слово — глагол?", ["летит", "синий", "окно"], "летит", topic_id),
        "noun_gender_number_case": lambda: make_choice_task("Слово “стол” какого рода?", ["мужского", "женского", "среднего"], "мужского", topic_id),
        "adjective_gender_number": lambda: make_choice_task("Как правильно: ___ лента", ["красная", "красный", "красное"], "красная", topic_id),
        "verb_tense": lambda: make_choice_task("Глагол “читал” какого времени?", ["прошедшего", "настоящего", "будущего"], "прошедшего", topic_id),
        "pronoun_intro": lambda: make_choice_task("Какое слово — местоимение?", ["он", "дом", "красный"], "он", topic_id),
        "sentence_homogeneous": lambda: make_choice_task("В предложении “Мама купила яблоки, груши и сливы” однородные слова:", ["яблоки, груши и сливы", "мама купила", "купила яблоки"], "яблоки, груши и сливы", topic_id),
        "text_plan_3": lambda: make_choice_task("Что помогает пересказать текст по частям?", ["план", "ударение", "алфавит"], "план", topic_id),
        "vocabulary_words_3": lambda: make_text_task("Вставь словарное слово: На станции находится __.", "вокзал", topic_id),
    }
    generator = generators.get(topic_id, generators["word_structure"])
    task = generate_unique_task(generator, used_questions)
    task["topic"] = topic_id
    task["topic_title"] = RUSSIAN_CLASS_3_TOPICS.get(topic_id, {}).get("title", "Русский язык 3 класс")
    return task
