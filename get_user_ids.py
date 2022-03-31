#!/usr/bin/env python3

import os
from pathlib import Path

import appdirs
import requests
import yaml

BASE_URL = "http://***REMOVED***/api/v2/users/find"
APIKEY = os.environ['APIKEY']

{"username": "Evandering"}

with open("users.txt") as f:
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


with open("ids.yaml", "w") as f:
    f.write(yaml.dump(ids))
