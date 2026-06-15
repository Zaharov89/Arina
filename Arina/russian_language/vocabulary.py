from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


FALLBACK_RUSSIAN_VOCABULARY = {
    1: [
        "русский язык", "ворона", "воробей", "пенал", "карандаш", "сорока", "собака", "ученик", "ученица",
        "учитель", "петух", "заяц", "корова", "молоко", "класс", "ребята", "тетради", "медведь",
        "мальчик", "девочка", "машина", "Москва", "спасибо", "Родина", "ветер", "рисунок", "рисовать",
        "яблоня", "яблоко", "берёза", "лопата", "ягода", "сахар", "посуда", "капуста", "одежда",
        "снегирь", "малина", "мороз", "иней", "коньки", "морковь", "сапоги", "отец", "фамилия",
        "Россия", "город", "улица", "стакан", "обед", "метро", "платок", "топор", "апрель",
    ],
    2: [
        "весело", "пальто", "хорошо", "деревня", "дежурный", "работа", "здравствуйте", "прощай",
        "сентябрь", "ветерок", "извини", "извините", "скоро", "быстро", "подлежащее", "сказуемое",
        "октябрь", "алфавит", "ноябрь", "до свидания", "земляника", "лягушка", "молоток", "урожай",
        "суббота", "декабрь", "мебель", "тарелка", "товарищ", "щавель", "метель", "народ", "вдруг",
        "завод", "обезьяна", "январь", "февраль", "картина", "магазин", "облако", "потому что", "так как",
    ],
    3: [
        "праздник", "вместе", "орех", "овёс", "восток", "пшеница", "заря", "понедельник", "погода",
        "трактор", "чёрный", "четыре", "восемь", "вторник", "среда", "картофель", "петрушка",
        "овощи", "горох", "огурец", "помидор", "огород", "компьютер", "столица", "творог", "обед",
        "ужин", "ракета", "шоссе", "пирог", "четверг", "север", "пороша", "чувство", "лестница",
        "интересный", "интересно", "коллектив", "коллекция", "аккуратно", "аккуратный", "грамм", "килограмм",
    ],
}


RUSSIAN_VOCABULARY_SELECT = text(
    """
    SELECT id, class_number, word, answer, is_active
    FROM arina.russian_vocabulary_words
    WHERE is_active = true
      AND (:class_number IS NULL OR class_number = :class_number)
    ORDER BY class_number, word
    """
)


def get_fallback_russian_vocabulary_words(class_number: int | None = None) -> list[dict]:
    class_numbers = [class_number] if class_number in FALLBACK_RUSSIAN_VOCABULARY else sorted(FALLBACK_RUSSIAN_VOCABULARY)
    result = []
    fallback_id = 1
    for current_class in class_numbers:
        for word in FALLBACK_RUSSIAN_VOCABULARY.get(current_class, []):
            result.append({"id": fallback_id, "class_number": current_class, "word": word, "answer": word, "is_active": True})
            fallback_id += 1
    return result


def get_russian_vocabulary_words(session: Session, class_number: int | None = None) -> list[dict]:
    try:
        rows = session.execute(RUSSIAN_VOCABULARY_SELECT, {"class_number": class_number}).mappings().all()
    except SQLAlchemyError:
        session.rollback()
        return get_fallback_russian_vocabulary_words(class_number)
    return [
        {"id": row["id"], "class_number": row["class_number"], "word": row["word"], "answer": row["answer"], "is_active": row["is_active"]}
        for row in rows
    ]


def get_russian_vocabulary_map(session: Session, class_number: int | None = None) -> dict[str, str]:
    return {item["word"]: item["answer"] for item in get_russian_vocabulary_words(session, class_number)}


def get_russian_vocabulary_word_list(session: Session, class_number: int | None = None) -> list[str]:
    return [item["word"] for item in get_russian_vocabulary_words(session, class_number)]
