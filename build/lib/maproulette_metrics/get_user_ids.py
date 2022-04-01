#!/usr/bin/env python3

import argparse
from pathlib import Path

import keyring
import requests
import yaml

BASE_URL = "http://***REMOVED***/api/v2/users/find"
APIKEY = keyring.get_password("maproulette", "")

def argparsing() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "output",
        type=Path,
        help="The location to save the list of ids to"
    )
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

def main():
    opts = argparsing()

    if opts.user:
        users = opts.user
    else:
        with opts.userlist.open() as f:
            users = set(f.read().splitlines())


    ids = {}
    for user in users:
        r = requests.get(
            BASE_URL,
            params={
                "username": user,
            },
            verify=False,
            headers={"apikey": APIKEY},
        )
        if not r.json():
            continue
        ids[user] = str(r.json()[0]["id"])


    with opts.output.open("w") as f:
        f.write(yaml.dump(ids))

if __name__ == "__main__":
    main()
