#!/usr/bin/env python3

import argparse
from datetime import date, timedelta
from pathlib import Path
from typing import Generator

import keyring
import pandas as pd
import requests
import yaml
from more_itertools import chunked

BASE_URL = "https://***REMOVED***/api/v2/data/{mtype}/leaderboard"
APIKEY = keyring.get_password("maproulette", "")
PAGE_LIMIT = 50

metric_type = {"editor": "user", "qc": "reviewer"}


def argparsing() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "ids",
        type=Path,
        help="The path to a yaml file containing usernames and their MR ids",
    )
    parser.add_argument(
        "output", type=xlsx_corrector, help="Where to save the output file."
    )
    parser.add_argument(
        "start",
        type=date.fromisoformat,
        help="The start of the date range you wish to check.",
    )
    parser.add_argument(
        "--end",
        type=date.fromisoformat,
        default=date.today(),
        help="The end of the date range you wish to check.",
    )
    parser.add_argument(
        "--metric-type",
        type=str.lower,
        choices=["editor", "qc"],
        default="editor",
        help="Which type of metrics to get: editor or QC. Defaults to editor.",
    )

    return parser.parse_args()


def daterange(start_date: date, end_date: date) -> Generator[date, None, None]:
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)


def xlsx_corrector(raw_path: str | Path) -> Path:
    """
    Fixes mistyped or missing xlsx extensions
    """
    raw_path = Path(raw_path)
    return raw_path.with_suffix(".xlsx")


def write_excel(df: pd.DataFrame, location: Path) -> None:
    with pd.ExcelWriter(
        location, engine="xlsxwriter", date_format="MM/DD/YY"
    ) as writer:
        df.to_excel(writer, index=True, freeze_panes=(1, 1))

        sheet = next(iter(writer.sheets.values()))

        for col_idx, (colname, column) in enumerate(df.reset_index().items()):
            colwidth = max(column.astype(str).str.len().max(), 8)
            sheet.set_column(col_idx, col_idx, colwidth)


def overwrite_confirm(location: Path) -> bool:
    response = input(f"{location} exists. Do you want to overwrite? N/y: ")
    return response.lower().startswith("y")


def main():
    opts = argparsing()
    mtype = metric_type[opts.metric_type]

    with opts.ids.open() as f:
        ids = yaml.safe_load(f.read())

    all_days = []
    for day in daterange(opts.start, opts.end + timedelta(1)):
        all_tasks = {}
        for page in chunked(ids.values(), PAGE_LIMIT):
            r = requests.get(
                BASE_URL.format(mtype=mtype),
                headers={"apikey": APIKEY},
                params={
                    "start": day.isoformat(),
                    "end": day.isoformat(),
                    "limit": PAGE_LIMIT,
                    "userIds": ",".join(page),
                },
                verify=False,
            )
            page_tasks = {
                record["name"]: record["completedTasks"] for record in r.json()
            }
            all_tasks |= page_tasks

        the_series = pd.Series(all_tasks)
        the_series.name = day
        all_days.append(the_series)

    # Creating a DataFrame this way results in dates along left axis and users along top,
    # hence the transpose
    df = pd.DataFrame(all_days).transpose()
    df.fillna(0, inplace=True)

    location: Path = opts.output
    if location.is_file() and not overwrite_confirm(location):
        print("Save aborted.")
        return
    write_excel(df, opts.output)


if __name__ == "__main__":
    main()
