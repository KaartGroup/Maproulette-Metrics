#!/usr/bin/env python3

import argparse
import os
from pathlib import Path
from typing import Iterable, Mapping

import appdirs
import keyring
import requests
import yaml

BASE_URL = os.get("MAPROULETTE_URL", "https://maproulette.org/")
API_PATH = "api/v2/users/find"
APIKEY = keyring.get_password("maproulette", "")
CACHE_DIR = Path(appdirs.user_cache_dir("Maproulette Metrics", "Kaart"))
CACHE_DIR.mkdir(exist_ok=True)


def argparsing() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    usergroup = parser.add_mutually_exclusive_group()
    usergroup.add_argument(
        "--userlist",
        type=Path,
        help="The location of a list of users to query"
    )
    usergroup.add_argument(
        "--user",
        nargs="+",
        help="A list of users to check, separated by spaces"
    )
    return parser.parse_args()


def get_single_user_id_from_api(user: str) -> str | None:
    r = requests.get(
        BASE_URL + API_PATH,
        headers={"apikey": APIKEY},
        params={"username": user},
        verify=False,
    )
    if r.json():
        return r.json()[0]["id"]


def get_user_ids_from_api(users: Iterable[str]) -> dict[str, str]:
    ids = {}
    for user in users:
        print(f"Getting numeric ID for user {user} from the server...", end="")
        if user_id := get_single_user_id_from_api(user):
            print(f"ID is {user_id}.")
            ids[user] = user_id
        else:
            print("User ID could not be retrieved.")
    return ids


def get_user_ids_with_caching(
    users: Iterable[str], save: bool = True
) -> dict[str, str]:
    """
    Gets user ids from the cache, downloads any needed ids from the cache
    """
    try:
        with (CACHE_DIR / "user_ids.yaml").open() as f:
            cached_ids = yaml.safe_load(f.read())
    except OSError:
        cached_ids = {}

    # Make sure only valid user IDs in the loaded dictionary
    cached_ids = {user: str(user_id) for user, user_id in cached_ids.items() if user_id}

    not_present = set(users) - set(cached_ids.keys())
    api_ids = get_user_ids_from_api(not_present)
    combined_ids = cached_ids | api_ids

    if (
        save
        and
        # Don't save if nothing new was loaded
        api_ids
    ):
        save_user_ids(combined_ids)

    return combined_ids


def save_user_ids(ids: Mapping[str, str]) -> None:
    with (CACHE_DIR / "user_ids.yaml").open("w") as f:
        f.write(yaml.dump(ids))


def main():
    opts = argparsing()

    if opts.user:
        users = set(opts.user)
    else:
        with opts.userlist.open() as f:
            users = set(f.read().splitlines())

    ids = get_user_ids_with_caching(users)


if __name__ == "__main__":
    main()
