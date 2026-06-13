"""Result storage service.

Current state:
- automatic saving is disabled;
- diary still reads data from Google Apps Script.

Future state:
- save test attempts to PostgreSQL;
- read diary/statistics from PostgreSQL;
- remove Google Apps Script dependency.
"""


def is_result_saving_enabled() -> bool:
    """Return False until PostgreSQL result storage is implemented."""
    return False
