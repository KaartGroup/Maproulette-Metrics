import argparse
from datetime import date
from pathlib import Path

from . import get_metrics
from .utils import xlsx_corrector


def argparsing() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="A script for checking metrics for given usernames"
    )
    parser.add_argument(
        "user_file",
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


def main():
    opts = vars(argparsing())
    opts["users"] = opts.userfile.read_text().splitlines()
    df = get_metrics.get_metrics(*opts)
    if (
        not opts["overwrite"]
        and opts["output"].is_file()
        and not overwrite_confirm(opts["output"])
    ):
        print("Save aborted.")
        return
    get_metrics.write_excel(df, location=opts["output"])


def overwrite_confirm(location: Path) -> bool:
    response = input(f"{location} exists. Do you want to overwrite? N/y: ")
    return response.lower().startswith("y")


if __name__ == "__main__":
    main()
