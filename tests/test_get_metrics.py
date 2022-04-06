from pathlib import Path

import pytest
from maproulette_metrics import get_metrics


@pytest.mark.parametrize(
    "uinput,corrected", [["test.xslx", Path("test.xlsx")], ["test", Path("test.xlsx")]]
)
def test_xlsx_connector(uinput: str, corrected: Path):
    assert get_metrics.xlsx_corrector(uinput) == corrected
