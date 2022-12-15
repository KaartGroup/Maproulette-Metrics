#!/usr/bin/env python3

import argparse
from datetime import date, timedelta
from pathlib import Path
from typing import Generator, Iterable, Literal

import keyring
import pandas as pd
import requests
from more_itertools import chunked

from . import BASE_URL, VERIFY_CERT
from .get_user_ids import get_user_ids_with_caching

API_PATH = "api/v2/data/{mtype}/leaderboard"
APIKEY = keyring.get_password(service_name="maproulette", username="")
PAGE_LIMIT = 50

metric_type = {"editor": "user", "qc": "reviewer"}


def argparsing() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="A script for checking metrics for given usernames"
    )
    parser.add_argument(
        "users",
        type=Path,
        help="The path to a textfile with a list of usernames to check",
    )
    parser.add_argument(
        "output", type=xlsx_corrector, help="Where to save the output file."
    )
    parser.add_argument(
        "start",
        type=date.fromisoformat,
        help="The start of the date range you wish to check, in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "end",
        type=date.fromisoformat,
        nargs="?",
        default=date.today(),
        help=(
            "(optional) The end of the date range you wish to check, in YYYY-MM-DD format. "
            "If not given, today's date will be used"
        ),
    )
    parser.add_argument(
        "-t",
        "--metric-type",
        type=str.lower,
        choices=["editor", "qc"],
        default="editor",
        help="Which type of metrics to get: editor or QC. Defaults to editor.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="If used, will overwrite existing files without asking.",
    )

    return parser.parse_args()


def daterange(start_date: date, end_date: date) -> Generator[date, None, None]:
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(days=n)


def xlsx_corrector(raw_path: str | Path) -> Path:
    """
    Fixes mistyped or missing xlsx extensions
    """
    raw_path = Path(raw_path)
    return raw_path.with_suffix(".xlsx")


def write_excel(df: pd.DataFrame, location: Path) -> None:
    with pd.ExcelWriter(location, engine="xlsxwriter", date_format="MMM D") as writer:
        df.to_excel(writer, index=True, freeze_panes=(1, 1))

        sheet = next(iter(writer.sheets.values()))

        for col_idx, (colname, column) in enumerate(df.reset_index().items()):
            colwidth = max(column.astype(str).str.len().max(), 6)
            sheet.set_column(col_idx, col_idx, colwidth)


def overwrite_confirm(location: Path) -> bool:
    response = input(f"{location} exists. Do you want to overwrite? N/y: ")
    return response.lower().startswith("y")


def get_user_page(
    users: Iterable,
    mtype: Literal["user", "qc"],
    start: date,
    end: date,
) -> dict:
    r = requests.get(
        url=(BASE_URL + API_PATH).format(mtype=mtype),
        headers={"apikey": APIKEY},
        params={
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": PAGE_LIMIT,
            "userIds": ",".join(str(user_id) for user_id in users),
        },
        verify=VERIFY_CERT,
    )
    r.raise_for_status()
    return {record["name"]: record["completedTasks"] for record in r.json()}


def main():
    opts = argparsing()
    mtype = metric_type[opts.metric_type]

    users = opts.users.read_text().splitlines()
    ids = get_user_ids_with_caching(users)

    df = pd.DataFrame(index=ids.keys())
    for day in daterange(opts.start, opts.end + timedelta(days=1)):
        start = end = day
        if day.weekday() == 0:
            # Monday, include prior Sunday's stats because of timezone difference
            start -= timedelta(days=1)
        elif day.weekday() == 4:
            # Friday, include following Saturday's stats because of timezone difference
            end += timedelta(days=1)
        elif day.weekday() >= 5:
            # Weekend; stats are included in days before and after, so we don't check these on their own
            continue

        day_tasks = {}
        for user_page in chunked(ids.values(), PAGE_LIMIT):
            day_tasks |= get_user_page(user_page, mtype, start, end)

        the_series = pd.Series(day_tasks)
        the_series.name = day
        df = pd.concat([df, the_series], axis=1)

    df.fillna(0, inplace=True)
    df.sort_index(inplace=True)

    location: Path = opts.output
    if not opts.overwrite and location.is_file() and not overwrite_confirm(location):
        print("Save aborted.")
        return
    write_excel(df, location=location)


if __name__ == "__main__":
    main()
