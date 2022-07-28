import argparse
from datetime import date
from pathlib import Path

from .utils import xlsx_corrector


def argparsing() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="A script for checking metrics for given usernames"
    )
    parser.add_argument(
        "users",
        type=Path,
        help="The path to a textfile with a list of usernames to check",
    )
    parser.add_argument(
        "output", type=xlsx_corrector, help="Where to save the output file."
    )
    parser.add_argument(
        "start",
        type=date.fromisoformat,
        help="The start of the date range you wish to check, in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "end",
        type=date.fromisoformat,
        nargs="?",
        default=date.today(),
        help=(
            "(optional) The end of the date range you wish to check, in YYYY-MM-DD format. "
            "If not given, today's date will be used"
        ),
    )
    parser.add_argument(
        "--metric-type",
        type=str.lower,
        choices=["editor", "qc"],
        default="editor",
        help="Which type of metrics to get: editor or QC. Defaults to editor.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="If used, will overwrite existing files without asking.",
    )

    return parser.parse_args()
