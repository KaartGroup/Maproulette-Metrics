import os

BASE_URL = os.getenv(key="MAPROULETTE_URL", default="https://maproulette.org/")
VERIFY_CERT = (
    os.getenv(
        key="MAPROULETTE_VERIFY_CERT",
        default="true",
    ).lower()
    != "false"
)
