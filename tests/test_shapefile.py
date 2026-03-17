from __future__ import annotations

import importlib.util
from types import SimpleNamespace

import pytest

from geo2dcat import convert
from geo2dcat.extractors.shapefile import extract_vector
from tests.conftest import FIXTURES_DIR


pytestmark = pytest.mark.skipif(importlib.util.find_spec("geopandas") is None, reason="geopandas not installed")


def test_convert_vector_fixture():
    fixture = FIXTURES_DIR / "sample.geojson"
    if not fixture.exists():
        pytest.skip("fixture not generated")
    result = convert(str(fixture))
    assert result["@type"] == "dcat:Dataset"
    assert isinstance(result["cf:variableMappings"], list)


def test_extract_vector_uses_attribute_count(monkeypatch, tmp_path):
    class FakeCRS:
        def to_string(self):
            return "EPSG:4326"

    class FakeSeries:
        def __init__(self, values):
            self.iloc = values

    class FakeGeoDataFrame:
        columns = ["name", "value", "geometry"]
        geometry = SimpleNamespace(name="geometry")
        total_bounds = (1.0, 2.0, 3.0, 4.0)
        crs = FakeCRS()
        geom_type = FakeSeries(["Point"])
        empty = False

    class FakeGeoPandas:
        @staticmethod
        def read_file(path, rows=1):
            return FakeGeoDataFrame()

    monkeypatch.setattr("geo2dcat.extractors.shapefile.optional_import", lambda *args, **kwargs: FakeGeoPandas())

    filepath = tmp_path / "sample.shp"
    filepath.write_text("", encoding="utf-8")
    metadata = extract_vector(str(filepath))

    assert metadata.get("description") == "Vector dataset with 2 attributes"
    assert [variable.get("name") for variable in metadata.get("variables", [])] == ["name", "value"]
    assert metadata.get("extra", {}).get("columns") == ["name", "value"]
