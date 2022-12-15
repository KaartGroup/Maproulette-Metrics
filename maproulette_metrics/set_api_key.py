#!/usr/bin/env python3

import getpass

import keyring


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

    keyring.set_password(service_name="maproulette", username="", password=apikey)
    print("API key successfully set!")


if __name__ == "__main__":
    main()
