#!/usr/bin/env python3

import getpass

import keyring


def main():
    apikey = ""
    while not apikey:
        apikey = getpass.getpass(
            "Paste your Maproulette API key (your input will be invisible, this is normal): "
        ).strip()
        if apikey:
            break
        print("No key was pasted.")

    keyring.set_password("maproulette", "", apikey)
    print("API key successfully set!")


if __name__ == "__main__":
    main()
