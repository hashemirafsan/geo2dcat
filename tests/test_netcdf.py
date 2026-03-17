from __future__ import annotations

import importlib.util

import pytest

from geo2dcat import convert
from tests.conftest import FIXTURES_DIR


pytestmark = pytest.mark.skipif(importlib.util.find_spec("netCDF4") is None, reason="netCDF4 not installed")


def test_convert_netcdf_fixture():
    fixture = FIXTURES_DIR / "sample.nc"
    if not fixture.exists():
        pytest.skip("fixture not generated")
    result = convert(str(fixture))
    assert result["@type"] == "dcat:Dataset"
    assert isinstance(result["cf:variableMappings"], list)
