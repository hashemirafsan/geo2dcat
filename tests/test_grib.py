from __future__ import annotations

import importlib.util

import pytest

from geo2dcat import convert
from tests.conftest import FIXTURES_DIR


pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("xarray") is None or importlib.util.find_spec("cfgrib") is None,
    reason="grib dependencies not installed",
)


def test_convert_grib_fixture():
    fixture = FIXTURES_DIR / "sample.grib2"
    if not fixture.exists():
        pytest.skip("real GRIB fixture not provided")
    result = convert(str(fixture))
    assert result["@type"] == "dcat:Dataset"
    assert isinstance(result["cf:variableMappings"], list)
