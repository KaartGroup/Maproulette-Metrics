#!/usr/bin/env python3

import argparse
import os
from datetime import date, timedelta
from pathlib import Path
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


if __name__ == "__main__":
    opts = argparsing()

    with opts.ids.open() as f:
        ids = yaml.safe_load(f.read())

    series_of_series = []
    for day in daterange(opts.start, opts.end + timedelta(1)):
        completed_tasks = {}
        for page in chunked(ids.values(), 50):
            r = requests.get(
                BASE_URL.format(mtype=metric_type[opts.metric_type]),
                headers={"apikey": APIKEY},
                params={
                    "start": day.isoformat(),
                    "end": (day).isoformat(),
                    "limit": 50,
                    "userIds": ",".join(page),
                },
                verify=False,
            )
            page_tasks = {
                record["name"]: record["completedTasks"] for record in r.json()
            }
            completed_tasks |= page_tasks
        the_series = pd.Series(completed_tasks)
        the_series.name = day
        series_of_series.append(the_series)

    df = pd.DataFrame(series_of_series)
    df = df.transpose()
    df.fillna(0, inplace=True)

    try:
        with opts.output.open("x") as f:
            df.to_excel(f)
    except FileExistsError:
        response = input(f"{opts.output} exists. Do you want to overwrite? N/y: ")
        if response.lower().startswith("y"):
            with opts.output.open("w") as f:
                df.to_excel(f)
        else:
            print("Save aborted.")
