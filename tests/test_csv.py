from __future__ import annotations

from geo2dcat.extractors.csv import extract_csv
from geo2dcat import convert
from tests.conftest import FIXTURES_DIR


def test_convert_csv_fixture():
    result = convert(str(FIXTURES_DIR / "sample.csv"))
    assert result["@type"] == "dcat:Dataset"
    assert "dcat" in result["@context"]
    assert isinstance(result["cf:variableMappings"], list)


def test_extract_csv_normalizes_unnamed_columns(tmp_path):
    filepath = tmp_path / "unnamed.csv"
    filepath.write_text(",TN,TG\n1,11.1,13.2\n2,5.4,11.0\n", encoding="utf-8")

    metadata = extract_csv(str(filepath))
    variables = metadata.get("variables", [])
    extra = metadata.get("extra", {})

    assert metadata.get("description") == "Tabular dataset with 3 columns"
    assert [variable.get("name") for variable in variables] == ["row_id", "TN", "TG"]
    assert extra.get("columns") == ["row_id", "TN", "TG"]
    assert extra.get("sample_rows", [])[0]["row_id"] == "1"
