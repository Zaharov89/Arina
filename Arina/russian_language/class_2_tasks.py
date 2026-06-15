import random

from Arina.russian_language.class_1_tasks import make_choice_task, make_text_task, make_number_task, generate_unique_task
from Arina.russian_language.class_2_topics import RUSSIAN_CLASS_2_TOPICS


TASKS_BY_TOPIC = {
    "sounds_letters_review": [
        lambda t: make_number_task("Сколько букв в слове “школа”?", 5, t),
        lambda t: make_number_task("Сколько звуков в слове “дом”?", 3, t),
        lambda t: make_choice_task("Что мы слышим и произносим?", ["звук", "буква", "слово"], "звук", t),
    ],
    "alphabet": [
        lambda t: make_choice_task("Какая буква идёт после Б?", ["А", "В", "Г"], "В", t),
        lambda t: make_choice_task("Какая буква идёт перед Д?", ["Г", "Е", "Ж"], "Г", t),
        lambda t: make_choice_task("Сколько букв в русском алфавите?", ["33", "32", "30"], "33", t),
    ],
    "vowels_consonants": [
        lambda t: make_choice_task("Выбери гласную букву:", ["м", "о", "т"], "о", t),
        lambda t: make_choice_task("Выбери согласную букву:", ["а", "у", "к"], "к", t),
        lambda t: make_choice_task("Какая буква гласная в слове “кот”?", ["о", "к", "т"], "о", t),
    ],
    "unstressed_vowels": [
        lambda t: make_choice_task("В каком слове есть безударная гласная?", ["трава", "дом", "мяч"], "трава", t),
        lambda t: make_choice_task("В слове “река” безударная гласная:", ["е", "а", "р"], "е", t),
        lambda t: make_choice_task("Безударную гласную нужно:", ["проверять", "пропускать", "заменять цифрой"], "проверять", t),
    ],
    "checked_unstressed_root": [
        lambda t: make_choice_task("Проверочное слово к слову “леса”:", ["лес", "лиса", "лесной"], "лес", t),
        lambda t: make_choice_task("Проверочное слово к слову “гора”:", ["горы", "горка", "горный"], "горы", t),
        lambda t: make_choice_task("Проверочное слово к слову “вода”:", ["воды", "водный", "водица"], "воды", t),
    ],
    "paired_consonants": [
        lambda t: make_choice_task("Проверочное слово к слову “гриб”:", ["грибы", "грибок", "грибной"], "грибы", t),
        lambda t: make_choice_task("Проверочное слово к слову “мороз”:", ["морозы", "морозный", "морозец"], "морозы", t),
        lambda t: make_choice_task("Проверочное слово к слову “сад”:", ["сады", "садик", "садовый"], "сады", t),
    ],
    "silent_consonants": [
        lambda t: make_choice_task("Где есть непроизносимая согласная?", ["солнце", "лиса", "дом"], "солнце", t),
        lambda t: make_choice_task("В каком слове есть непроизносимая согласная?", ["сердце", "море", "окно"], "сердце", t),
        lambda t: make_choice_task("Проверочное слово к “солнце”:", ["солнышко", "сон", "соль"], "солнышко", t),
    ],
    "separating_soft_sign": [
        lambda t: make_choice_task("В каком слове есть разделительный мягкий знак?", ["семья", "конь", "мел"], "семья", t),
        lambda t: make_choice_task("В каком слове мягкий знак разделительный?", ["вьюга", "день", "конь"], "вьюга", t),
        lambda t: make_choice_task("Разделительный мягкий знак пишется:", ["между согласной и гласной", "в конце каждого слова", "после цифры"], "между согласной и гласной", t),
    ],
    "noun": [
        lambda t: make_choice_task("Какое слово — имя существительное?", ["бежит", "зелёный", "книга"], "книга", t),
        lambda t: make_choice_task("Имя существительное отвечает на вопрос:", ["кто? что?", "какой?", "что делает?"], "кто? что?", t),
        lambda t: make_choice_task("Какое слово называет предмет?", ["стол", "идёт", "синий"], "стол", t),
    ],
    "adjective": [
        lambda t: make_choice_task("Какое слово — имя прилагательное?", ["красивый", "пишет", "ручка"], "красивый", t),
        lambda t: make_choice_task("Прилагательное отвечает на вопрос:", ["какой?", "кто?", "что делает?"], "какой?", t),
        lambda t: make_choice_task("Какое слово называет признак?", ["весёлый", "дом", "читает"], "весёлый", t),
    ],
    "verb": [
        lambda t: make_choice_task("Какое слово — глагол?", ["читает", "синий", "окно"], "читает", t),
        lambda t: make_choice_task("Глагол отвечает на вопрос:", ["что делает?", "кто?", "какой?"], "что делает?", t),
        lambda t: make_choice_task("Какое слово называет действие?", ["прыгает", "зелёный", "книга"], "прыгает", t),
    ],
    "sentence_members": [
        lambda t: make_choice_task("В предложении “Мальчик рисует.” сказуемое:", ["мальчик", "рисует", "предложение"], "рисует", t),
        lambda t: make_choice_task("В предложении “Птица летит.” подлежащее:", ["птица", "летит", "быстро"], "птица", t),
        lambda t: make_choice_task("Сказуемое чаще всего выражено:", ["глаголом", "числом", "предлогом"], "глаголом", t),
    ],
    "text_theme": [
        lambda t: make_choice_task("Если текст рассказывает о зиме, его тема:", ["зима", "лето", "школа"], "зима", t),
        lambda t: make_choice_task("Тема текста — это:", ["о чём говорится", "количество букв", "первая буква"], "о чём говорится", t),
        lambda t: make_choice_task("Заголовок должен отражать:", ["тему текста", "только последнюю букву", "номер страницы"], "тему текста", t),
    ],
    "vocabulary_words_2": [
        lambda t: make_text_task("Напиши словарное слово: первый осенний месяц.", "сентябрь", t),
        lambda t: make_text_task("Напиши словарное слово: предмет для еды — __.", "тарелка", t),
        lambda t: make_text_task("Напиши словарное слово: место, где живут люди за городом — __.", "деревня", t),
    ],
}


def generate_russian_class_2_topic_task(topic_id: str, used_questions: list[str] | None = None) -> dict:
    tasks = TASKS_BY_TOPIC.get(topic_id, TASKS_BY_TOPIC["sounds_letters_review"])
    task = generate_unique_task(lambda: random.choice(tasks)(topic_id), used_questions)
    task["topic"] = topic_id
    task["topic_title"] = RUSSIAN_CLASS_2_TOPICS.get(topic_id, {}).get("title", "Русский язык 2 класс")
    return task
