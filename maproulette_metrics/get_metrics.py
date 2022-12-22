#!/usr/bin/env python3

import argparse
from datetime import date, timedelta
from math import ceil
from pathlib import Path
from typing import Generator, Iterable, Literal

import pandas as pd
import requests
from more_itertools import chunked

from . import BASE_URL, VERIFY_CERT
from .get_user_ids import get_user_ids_with_caching
from .utils import daterange, get_api_key

API_PATH = "api/v2/data/{mtype}/leaderboard"
APIKEY = get_api_key()
PAGE_LIMIT = 50

METRIC_TYPE_TABLE = {"editor": "user", "qc": "reviewer"}


def write_excel(df: pd.DataFrame, location: Path) -> None:
    with pd.ExcelWriter(location, engine="xlsxwriter", date_format="MMM D") as writer:
        df.to_excel(writer, index=True, freeze_panes=(1, 1))

        sheet = next(iter(writer.sheets.values()))

        for col_idx, (colname, column) in enumerate(df.reset_index().items()):
            colwidth = max(column.astype(str).str.len().max(), 6)
            sheet.set_column(col_idx, col_idx, colwidth)


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


class MetricGetter:
    def __init__(self) -> None:
        self.cur_iteration = 0
        self.max_iterations = 0
        self.cur_date = None
        self.page = 0
        self.page_count = 0

    def get_metrics(
        self,
        users: Iterable[str],
        start: date,
        end: date,
        metric_type: Literal["editor", "qc"],
        apikey: str,
        **kwargs,
    ) -> pd.DataFrame:
        mtype = METRIC_TYPE_TABLE[metric_type]

        ids = get_user_ids_with_caching(users)
        self.page_count = ceil(len(ids.values()) / PAGE_LIMIT)

        self.max_iterations = (end - start).days * self.page_count

        df = pd.DataFrame(index=ids.keys())
        for day in daterange(start, end + timedelta(days=1)):
            self.cur_date = day
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
            for iteration, user_page in enumerate(chunked(ids.values(), PAGE_LIMIT)):
                self.page = iteration
                self.cur_iteration += 1
                try:
                    day_tasks |= get_user_page(
                        users=user_page, mtype=mtype, start=start, end=end
                    )
                except Exception:
                    continue

            the_series = pd.Series(day_tasks, dtype=int)
            the_series.name = day
            df = pd.concat([df, the_series], axis=1)

        self.cur_iteration = self.max_iterations
        df.fillna(0, inplace=True)
        df.sort_index(inplace=True)

        return df
