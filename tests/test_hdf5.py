from __future__ import annotations

import importlib.util

import pytest

from geo2dcat import convert
from tests.conftest import FIXTURES_DIR


pytestmark = pytest.mark.skipif(importlib.util.find_spec("h5py") is None, reason="h5py not installed")


def test_convert_hdf5_fixture():
    fixture = FIXTURES_DIR / "sample.h5"
    if not fixture.exists():
        pytest.skip("fixture not generated")
    result = convert(str(fixture))
    assert result["@type"] == "dcat:Dataset"
    assert isinstance(result["cf:variableMappings"], list)
