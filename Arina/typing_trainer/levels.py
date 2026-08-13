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
        {"level": 1, "title": "А и О", "letters": ["А", "О"], "total_letters": 20, "required_accuracy": 80},
        {"level": 2, "title": "А, О, В, Л", "letters": ["А", "О", "В", "Л"], "total_letters": 24, "required_accuracy": 80},
        {"level": 3, "title": "Добавляем Ы и Д", "letters": ["А", "О", "В", "Л", "Ы", "Д"], "total_letters": 28, "required_accuracy": 82},
        {"level": 4, "title": "Домашний ряд", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж"], "total_letters": 32, "required_accuracy": 85},
        {"level": 5, "title": "П и Р", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж", "П", "Р"], "total_letters": 34, "required_accuracy": 85},
        {"level": 6, "title": "К и Е", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж", "П", "Р", "К", "Е"], "total_letters": 36, "required_accuracy": 86},
        {"level": 7, "title": "М и И", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж", "П", "Р", "К", "Е", "М", "И"], "total_letters": 38, "required_accuracy": 86},
        {"level": 8, "title": "С и Т", "letters": ["Ф", "Ы", "В", "А", "О", "Л", "Д", "Ж", "П", "Р", "К", "Е", "М", "И", "С", "Т"], "total_letters": 40, "required_accuracy": 88},
    ],
    "en": [
        {"level": 1, "title": "F and J", "letters": ["F", "J"], "total_letters": 20, "required_accuracy": 80},
        {"level": 2, "title": "F, J, D, K", "letters": ["F", "J", "D", "K"], "total_letters": 24, "required_accuracy": 80},
        {"level": 3, "title": "S and L", "letters": ["F", "J", "D", "K", "S", "L"], "total_letters": 28, "required_accuracy": 82},
        {"level": 4, "title": "Home row", "letters": ["A", "S", "D", "F", "J", "K", "L", ";"], "total_letters": 32, "required_accuracy": 85},
        {"level": 5, "title": "E and I", "letters": ["A", "S", "D", "F", "J", "K", "L", ";", "E", "I"], "total_letters": 34, "required_accuracy": 85},
        {"level": 6, "title": "R and U", "letters": ["A", "S", "D", "F", "J", "K", "L", ";", "E", "I", "R", "U"], "total_letters": 36, "required_accuracy": 86},
        {"level": 7, "title": "T and Y", "letters": ["A", "S", "D", "F", "J", "K", "L", ";", "E", "I", "R", "U", "T", "Y"], "total_letters": 38, "required_accuracy": 86},
        {"level": 8, "title": "C and M", "letters": ["A", "S", "D", "F", "J", "K", "L", ";", "E", "I", "R", "U", "T", "Y", "C", "M"], "total_letters": 40, "required_accuracy": 88},
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
