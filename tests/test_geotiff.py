from __future__ import annotations

import importlib.util

import pytest

from geo2dcat import convert
from tests.conftest import FIXTURES_DIR


pytestmark = pytest.mark.skipif(importlib.util.find_spec("rasterio") is None, reason="rasterio not installed")


def test_convert_geotiff_fixture():
    fixture = FIXTURES_DIR / "sample.tif"
    if not fixture.exists():
        pytest.skip("fixture not generated")
    result = convert(str(fixture))
    assert result["@type"] == "dcat:Dataset"
    assert result["dct:spatial"]["geo:asWKT"]["@value"].startswith("POLYGON(")
