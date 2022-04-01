#!/usr/bin/env python3

import argparse
import os
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Generator

import pandas as pd
import requests
import yaml

BASE_URL = "https://***REMOVED***/api/v2/data/user/{user}/leaderboard"
APIKEY = os.environ["APIKEY"]


def argparsing() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "ids",
        type=Path,
        help="The path to a yaml file containing usernames and their MR ids",
    )
    parser.add_argument("output", type=Path, help="Where to save the output file.")
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

    return parser.parse_args()


def daterange(start_date: date, end_date: date) -> Generator[date, None, None]:
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)

if __name__ == "__main__":
    opts = argparsing()

    with opts.ids.open() as f:
        ids = yaml.safe_load(f.read())

    series_of_series = []
    for username, user in ids.items():
        daily_tasks = pd.Series()
        daily_tasks.name = username
        for day in daterange(opts.start, opts.end + timedelta(1)):
            r = requests.get(
                BASE_URL.format(user=user),
                headers={"apikey": APIKEY},
                params={"start": day.isoformat(), "end": (day).isoformat()},
                verify=False,
            )
            try:
                completed_tasks = r.json()[0]["completedTasks"]
            except IndexError:
                completed_tasks = 0
            daily_tasks[day] = completed_tasks
            time.sleep(0.5)
        series_of_series.append(daily_tasks)

    df = pd.DataFrame(series_of_series)

    df.to_excel(opts.output)
