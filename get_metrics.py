#!/usr/bin/env python3

import argparse
import os
from datetime import date, timedelta
from typing import Generator

import pandas as pd
import requests
import yaml
from more_itertools import chunked

BASE_URL = "https://***REMOVED***/api/v2/data/{mtype}/leaderboard"
APIKEY = os.environ["APIKEY"]

metric_type = {"editor": "user", "qc": "reviewer"}


def argparsing() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
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


opts = argparsing()

with open("ids.yaml") as f:
    ids = yaml.safe_load(f.read())

series_of_series = []
for username, user in ids.items():
    daily_tasks = pd.Series()
    daily_tasks.name = username
    for day in daterange(opts.start, opts.end):
        r = requests.get(
            BASE_URL.format(user=user),
            headers={"apikey": APIKEY},
            params={"start": day.isoformat(), "end": (day + timedelta(1)).isoformat()},
            verify=False,
        )
        try:
            completed_tasks = r.json()[0]["completedTasks"]
        except IndexError:
            completed_tasks = 0
        daily_tasks[day] = completed_tasks
        time.sleep(1)
    series_of_series.append(daily_tasks)

    with opts.ids.open() as f:
        ids = yaml.safe_load(f.read())
df = pd.DataFrame(series_of_series)

df.to_excel(
    "metrics.xlsx"
)
