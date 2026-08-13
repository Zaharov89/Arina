LAYOUT_TITLES = {
    "ru": "Русская раскладка",
    "en": "Английская раскладка",
}

ANIMALS = {
    "dino": {"title": "Динозаврик", "emoji": "🦖"},
    "cat": {"title": "Котёнок", "emoji": "🐱"},
    "dog": {"title": "Собачка", "emoji": "🐶"},
}

HAND_POSITIONS = {
    "ru": {
        "left": [("мизинец", "Ф"), ("безымянный", "Ы"), ("средний", "В"), ("указательный", "А")],
        "right": [("указательный", "О"), ("средний", "Л"), ("безымянный", "Д"), ("мизинец", "Ж")],
        "home_row": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж"],
        "hint": "На физической клавиатуре указательные пальцы стоят на клавишах А и О. Большие пальцы лежат на пробеле.",
    },
    "en": {
        "left": [("little finger", "A"), ("ring finger", "S"), ("middle finger", "D"), ("index finger", "F")],
        "right": [("index finger", "J"), ("middle finger", "K"), ("ring finger", "L"), ("little finger", ";")],
        "home_row": ["A", "S", "D", "F", "J", "K", "L", ";"],
        "hint": "Index fingers stay on F and J. These keys usually have small bumps so fingers can find the home row without looking.",
    },
}

TYPING_LEVELS = {
    "ru": [
        {"level": 1, "kind": "letters", "title": "А и О", "letters": ["А", "О"], "total_letters": 20, "required_accuracy": 80},
        {"level": 2, "kind": "letters", "title": "А, О, В, Л", "letters": ["А", "О", "В", "Л"], "total_letters": 24, "required_accuracy": 80},
        {"level": 3, "kind": "letters", "title": "Добавляем Ы и Д", "letters": ["А", "О", "В", "Л", "Ы", "Д"], "total_letters": 28, "required_accuracy": 82},
        {"level": 4, "kind": "letters", "title": "Домашний ряд", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж"], "total_letters": 32, "required_accuracy": 85},
        {"level": 5, "kind": "letters", "title": "П и Р", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж", "П", "Р"], "total_letters": 34, "required_accuracy": 85},
        {"level": 6, "kind": "letters", "title": "К и Е", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж", "П", "Р", "К", "Е"], "total_letters": 36, "required_accuracy": 86},
        {"level": 7, "kind": "letters", "title": "М и И", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж", "П", "Р", "К", "Е", "М", "И"], "total_letters": 38, "required_accuracy": 86},
        {"level": 8, "kind": "letters", "title": "С и Т", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж", "П", "Р", "К", "Е", "М", "И", "С", "Т"], "total_letters": 40, "required_accuracy": 88},
        {"level": 9, "kind": "chunks", "title": "Первые слоги", "letters": ["А", "О", "В", "Л", "М", "И"], "chunks": ["МА", "МО", "МИ", "ЛА", "ЛО", "ВА", "ВО"], "total_letters": 24, "required_accuracy": 88},
        {"level": 10, "kind": "chunks", "title": "Слоги домашнего ряда", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж"], "chunks": ["ВА", "ВО", "ЛА", "ЛО", "ДА", "ДО", "ЖА"], "total_letters": 28, "required_accuracy": 90},
        {"level": 11, "kind": "words", "title": "Короткие слова", "letters": ["А", "О", "В", "Л", "М", "И", "С", "Т"], "chunks": ["МАМА", "ЛАМА", "МАЛО", "ВОЛ", "МИЛА", "САМ", "ТОМ"], "total_letters": 24, "required_accuracy": 90},
        {"level": 12, "kind": "words", "title": "Слова домашнего ряда", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж", "М", "И", "С", "Т"], "chunks": ["ДОМ", "ЛАД", "ВОДА", "ДАЛА", "ЖАЛО", "САД", "МОДА"], "total_letters": 26, "required_accuracy": 92},
    ],
    "en": [
        {"level": 1, "kind": "letters", "title": "F and J", "letters": ["F", "J"], "total_letters": 20, "required_accuracy": 80},
        {"level": 2, "kind": "letters", "title": "F, J, D, K", "letters": ["F", "J", "D", "K"], "total_letters": 24, "required_accuracy": 80},
        {"level": 3, "kind": "letters", "title": "S and L", "letters": ["F", "J", "D", "K", "S", "L"], "total_letters": 28, "required_accuracy": 82},
        {"level": 4, "kind": "letters", "title": "Home row", "letters": ["A", "S", "D", "F", "J", "K", "L", ";"], "total_letters": 32, "required_accuracy": 85},
        {"level": 5, "kind": "letters", "title": "E and I", "letters": ["A", "S", "D", "F", "J", "K", "L", ";", "E", "I"], "total_letters": 34, "required_accuracy": 85},
        {"level": 6, "kind": "letters", "title": "R and U", "letters": ["A", "S", "D", "F", "J", "K", "L", ";", "E", "I", "R", "U"], "total_letters": 36, "required_accuracy": 86},
        {"level": 7, "kind": "letters", "title": "T and Y", "letters": ["A", "S", "D", "F", "J", "K", "L", ";", "E", "I", "R", "U", "T", "Y"], "total_letters": 38, "required_accuracy": 86},
        {"level": 8, "kind": "letters", "title": "C and M", "letters": ["A", "S", "D", "F", "J", "K", "L", ";", "E", "I", "R", "U", "T", "Y", "C", "M"], "total_letters": 40, "required_accuracy": 88},
        {"level": 9, "kind": "chunks", "title": "First syllables", "letters": ["A", "S", "D", "F", "J", "K", "L"], "chunks": ["FA", "JA", "LA", "SA", "DA", "KA"], "total_letters": 24, "required_accuracy": 88},
        {"level": 10, "kind": "chunks", "title": "Short letter groups", "letters": ["A", "S", "D", "F", "J", "K", "L", "E", "I"], "chunks": ["FAD", "JAK", "LAD", "KID", "FALL", "DILL"], "total_letters": 30, "required_accuracy": 90},
        {"level": 11, "kind": "words", "title": "Short words", "letters": ["A", "S", "D", "F", "J", "K", "L", "E", "I", "C", "M"], "chunks": ["DAD", "KID", "FALL", "SAIL", "MILK", "LAKE", "CALL"], "total_letters": 26, "required_accuracy": 90},
        {"level": 12, "kind": "words", "title": "Easy words", "letters": ["A", "S", "D", "F", "J", "K", "L", "E", "I", "C", "M", "T", "Y"], "chunks": ["CAT", "MAY", "DAY", "TELL", "CITY", "TIME", "SILK"], "total_letters": 28, "required_accuracy": 92},
    ],
}


def get_layout_levels(layout_code: str) -> list[dict]:
    return TYPING_LEVELS.get(layout_code, TYPING_LEVELS["ru"])


def get_level(layout_code: str, level_number: int) -> dict:
    levels = get_layout_levels(layout_code)
    for level in levels:
        if level["level"] == level_number:
            return level
    return levels[0]


def get_max_level(layout_code: str) -> int:
    return max(level["level"] for level in get_layout_levels(layout_code))
