from __future__ import annotations

import json

from geo2dcat.cli import main
from tests.conftest import FIXTURES_DIR


def test_cli_convert_stdout(capsys):
    exit_code = main(["convert", str(FIXTURES_DIR / "sample.csv")])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["@type"] == "dcat:Dataset"


def test_cli_lookup(capsys):
    exit_code = main(["lookup", "t2m"])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert payload["cf_standard_name"] == "air_temperature"
