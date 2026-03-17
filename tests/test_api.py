from __future__ import annotations

import json

from geo2dcat import batch_convert, convert_to_file
from tests.conftest import FIXTURES_DIR


def test_convert_to_file(tmp_path):
    output = tmp_path / "out.jsonld"
    result_path = convert_to_file(str(FIXTURES_DIR / "sample.csv"), str(output))
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert result_path == str(output)
    assert payload["@type"] == "dcat:Dataset"


def test_batch_convert(tmp_path):
    sample = tmp_path / "sample.csv"
    sample.write_text("a,b\n1,2\n", encoding="utf-8")
    results = batch_convert(str(tmp_path))
    assert len(results) == 1
    assert results[0]["status"] == "ok"
