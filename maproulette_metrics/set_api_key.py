#!/usr/bin/env python3

import getpass

from .utils import set_api_key


def main():
    apikey = ""
    while not apikey:
        apikey = getpass.getpass(
            prompt="Paste your Maproulette API key "
            "(your input will be invisible, this is normal) "
            "Use CTRL-C on your keyboard to cancel: "
        ).strip()
        if apikey:
            break
        print("No key was pasted.")

    set_api_key(apikey)
    print("API key successfully set!")


if __name__ == "__main__":
    main()
