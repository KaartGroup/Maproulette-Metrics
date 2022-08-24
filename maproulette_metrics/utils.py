import functools
from datetime import date, timedelta
from pathlib import Path
from typing import Generator

import keyring


def xlsx_corrector(raw_path: str | Path) -> Path:
    """
    Fixes mistyped or missing xlsx extensions
    """
    raw_path = Path(raw_path)
    return raw_path.with_suffix(".xlsx")


def daterange(start_date: date, end_date: date) -> Generator[date, None, None]:
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(days=n)


def dirname(the_path: str | Path) -> Path:
    """
    Return the path of the nearest directory,
    which can be the same as input if it is
    already a directory or else the parent
    """
    the_path = Path(the_path)
    return the_path if the_path.is_dir() else the_path.parent


set_api_key = functools.partial(
    keyring.set_password, service_name="maproulette", username="default"
)

get_api_key = functools.partial(
    keyring.get_password, service_name="maproulette", username="default"
)
