import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
import os
from datetime import datetime

# Убраны лишние пробелы
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Путь к credentials.json — по умолчанию в корне проекта
CREDENTIALS_PATH = "credentials.json"

# ID таблицы — замените на ваш реальный ID
SPREADSHEET_ID = "179BbOfZhKpliE0uN81shYmEUXcZRotqvfPoKOEZUaGc"

# Структура предметов
SUBJECTS = {
    "russian": {
        "start_row": 2,
        "name_cell": "L2",
        "month_cols": [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11),
                       (12, 13), (14, 15), (16, 17), (18, 19), (20, 21), (22, 23)],
        "summary": {
            "month_avg": "B38",
            "month_days": "B39",
            "year_avg": "B42",
            "year_days": "B43"
        }
    },
    "english": {
        "start_row": 48,
        "name_cell": "L48",
        "month_cols": [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11),
                       (12, 13), (14, 15), (16, 17), (18, 19), (20, 21), (22, 23)],
        "summary": {
            "month_avg": "B84",
            "month_days": "B85",
            "year_avg": "B88",
            "year_days": "B89"
        }
    },
    "math": {
        "start_row": 94,
        "name_cell": "L94",
        "month_cols": [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11),
                       (12, 13), (14, 15), (16, 17), (18, 19), (20, 21), (22, 23)],
        "summary": {
            "month_avg": "B130",
            "month_days": "B131",
            "year_avg": "B134",
            "year_days": "B135"
        }
    }
}

class GoogleSheetClient:
    def __init__(self):
        self._client = None
        self._sheet = None

    def _connect(self):
        if self._client is None:
            try:
                creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
                self._client = gspread.authorize(creds)
                self._sheet = self._client.open_by_key(SPREADSHEET_ID).worksheet("Арина")
            except Exception as e:
                raise Exception(f"Ошибка подключения к Google Таблице: {e}")
        return self._sheet

    def save_result(self, result):
        sheet = self._connect()
        today = datetime.now().date()
        month = today.month
        day = today.day

        subject_info = SUBJECTS[result.subject]
        start_row = subject_info["start_row"]
        month_col_pair = subject_info["month_cols"][month - 1]

        date_col = month_col_pair[0] + 1
        date_col_letter = chr(ord('A') + date_col - 1)
        target_row = None

        for row in range(start_row, start_row + 31):
            cell_value = sheet.cell(row, date_col).value
            if cell_value and cell_value.strip() == str(today):
                target_row = row
                break

        if target_row is None:
            raise ValueError(f"Не найдена дата {today} для предмета {result.subject}")

        grade_col = month_col_pair[1] + 1
        sheet.update_cell(target_row, grade_col, result.score_percent)

    def get_summary(self, subject: str) -> Dict[str, Any]:
        sheet = self._connect()
        subject_info = SUBJECTS[subject]
        summary = subject_info["summary"]

        data = {}
        for key, cell in summary.items():
            value = sheet.acell(cell).value
            if value == "#DIV/0!":
                value = 0
            try:
                data[key] = float(value) if '.' in value else int(value)
            except (ValueError, TypeError):
                data[key] = 0

        return data
