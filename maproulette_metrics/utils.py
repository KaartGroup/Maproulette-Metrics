from datetime import date, timedelta
from pathlib import Path
from typing import Generator


def xlsx_corrector(raw_path: str | Path) -> Path:
    """
    Fixes mistyped or missing xlsx extensions
    """
    raw_path = Path(raw_path)
    return raw_path.with_suffix(".xlsx")


def daterange(start_date: date, end_date: date) -> Generator[date, None, None]:
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(days=n)
