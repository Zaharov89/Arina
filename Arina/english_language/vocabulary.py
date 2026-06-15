from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


FALLBACK_ENGLISH_VOCABULARY = {
    2: [
        ("Sheep", "Овца", "[ʃiːp]"), ("Fish", "Рыба", "[fɪʃ]"), ("Ship", "Корабль", "[ʃɪp]"),
        ("Chick", "Цыплёнок", "[tʃɪk]"), ("Cheese", "Сыр", "[tʃiːz]"), ("Brother", "Брат", "[ˈbrʌðə]"),
        ("Sister", "Сестра", "[ˈsɪstə]"), ("School", "Школа", "[skuːl]"), ("Pen", "Ручка", "[pen]"),
        ("Book", "Книга", "[bʊk]"), ("Pencil", "Карандаш", "[ˈpensl]"), ("Family", "Семья", "[ˈfæməli]"),
        ("Red", "Красный", "[red]"), ("Yellow", "Жёлтый", "[ˈjeləʊ]"), ("Green", "Зелёный", "[ɡriːn]"),
        ("Blue", "Синий", "[bluː]"), ("House", "Дом", "[haʊs]"), ("Kitchen", "Кухня", "[ˈkɪtʃɪn]"),
        ("Apple", "Яблоко", "[ˈæpl]"), ("Milk", "Молоко", "[mɪlk]"), ("One", "Один", "[wʌn]"),
        ("Two", "Два", "[tuː]"), ("Five", "Пять", "[faɪv]"), ("Ten", "Десять", "[ten]"),
    ],
    3: [
        ("Holiday", "Каникулы", "[ˈhɒlədeɪ]"), ("Winter", "Зима", "[ˈwɪntə]"), ("Autumn", "Осень", "[ˈɔːtəm]"),
        ("Summer", "Лето", "[ˈsʌmə]"), ("Spring", "Весна", "[sprɪŋ]"), ("Socks", "Носки", "[sɒks]"),
        ("T-shirt", "Футболка", "[ˈtiː ʃɜːt]"), ("School bag", "Портфель", "[skuːl bæɡ]"),
        ("Ruler", "Линейка", "[ˈruːlə]"), ("Thirteen", "Тринадцать", "[ˌθɜːˈtiːn]"),
        ("Twenty", "Двадцать", "[ˈtwenti]"), ("English", "Английский язык", "[ˈɪŋɡlɪʃ]"),
        ("Maths", "Математика", "[mæθs]"), ("History", "История", "[ˈhɪstri]"), ("I", "Я", "[aɪ]"),
        ("You", "Ты", "[juː]"), ("We", "Мы", "[wiː]"), ("They", "Они", "[ðeɪ]"),
        ("Chicken", "Курица", "[ˈtʃɪkɪn]"), ("Water", "Вода", "[ˈwɔːtə]"), ("Potato", "Картофель", "[pəˈteɪtəʊ]"),
        ("Carrot", "Морковь", "[ˈkærət]"), ("Ball", "Мяч", "[bɔːl]"), ("Train", "Поезд", "[treɪn]"),
    ],
}


ENGLISH_VOCABULARY_SELECT = text(
    """
    SELECT id, class_number, english_word, russian_translation, transcription, is_active
    FROM arina.english_vocabulary_words
    WHERE is_active = true
      AND (:class_number IS NULL OR class_number = :class_number)
    ORDER BY class_number, english_word
    """
)


def build_word_item(item_id: int, class_number: int, english_word: str, russian_translation: str, transcription: str = "") -> dict:
    return {"id": item_id, "class_number": class_number, "en": [english_word], "ru": [russian_translation], "transcription": [transcription or ""], "english_word": english_word, "russian_translation": russian_translation, "is_active": True}


def get_fallback_english_vocabulary_words(class_number: int | None = None) -> list[dict]:
    class_numbers = [class_number] if class_number in FALLBACK_ENGLISH_VOCABULARY else sorted(FALLBACK_ENGLISH_VOCABULARY)
    result = []
    item_id = 1
    for current_class in class_numbers:
        for english_word, russian_translation, transcription in FALLBACK_ENGLISH_VOCABULARY.get(current_class, []):
            result.append(build_word_item(item_id, current_class, english_word, russian_translation, transcription))
            item_id += 1
    return result


def get_english_vocabulary_words(session: Session, class_number: int | None = None) -> list[dict]:
    try:
        rows = session.execute(ENGLISH_VOCABULARY_SELECT, {"class_number": class_number}).mappings().all()
    except SQLAlchemyError:
        session.rollback()
        return get_fallback_english_vocabulary_words(class_number)
    return [build_word_item(row["id"], row["class_number"], row["english_word"], row["russian_translation"], row["transcription"] or "") | {"is_active": row["is_active"]} for row in rows]
