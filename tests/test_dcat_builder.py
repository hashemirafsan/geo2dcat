from __future__ import annotations

from typing import cast

from geo2dcat.dcat_builder import DCAT_CONTEXT, build_dcat_dataset
from geo2dcat.types import NormalizedMetadata


def test_build_dcat_dataset_structure(tmp_path):
    source = tmp_path / "era5_temp.nc"
    source.write_text("placeholder", encoding="utf-8")
    metadata = {
        "format": "NetCDF",
        "title": "ERA5 temperature",
        "description": "Test dataset",
        "institution": "ECMWF",
        "creator": "Analyst",
        "creator_email": "analyst@example.com",
        "license": "cc-by-4.0",
        "references": "https://doi.org/example",
        "history": "generated from fixture",
        "conventions": ["CF-1.8"],
        "bbox_wkt": "POLYGON((20 10, 21 10, 21 11, 20 11, 20 10))",
        "time_start": "2024-01-01T00:00:00Z",
        "time_end": "2024-01-02T00:00:00Z",
        "crs": "EPSG:4326",
        "variables": [
            {
                "name": "t2m",
                "standard_name": None,
                "long_name": "2 metre temperature",
                "units": "K",
                "shape": [2, 2, 2],
                "dimensions": ["time", "lat", "lon"],
            }
        ],
        "extra": {"source": "test"},
    }

    result = build_dcat_dataset(str(source), cast(NormalizedMetadata, metadata))

    assert result["@type"] == "dcat:Dataset"
    assert result["@context"] == DCAT_CONTEXT
    assert result["dct:format"] == "NetCDF"
    assert result["cf:variableMappings"][0]["cf:standardName"] == "air_temperature"
    assert result["cf:ontologyMappings"][0]["@id"] == "sweet:AirTemperature"
    assert result["dcat:theme"][0]["@id"] == "theme:AtmosphericConditions"


def test_build_dcat_dataset_infers_dataset_theme_from_context(tmp_path):
    source = tmp_path / "grc_population_2015.tif"
    source.write_text("placeholder", encoding="utf-8")
    metadata = {
        "format": "GeoTIFF",
        "title": "GRC population 2015",
        "description": "Population distribution raster for Greece",
        "variables": [
            {
                "name": "band_1",
                "standard_name": None,
                "long_name": "population density",
                "units": None,
                "shape": [10, 10],
                "dimensions": ["y", "x"],
            }
        ],
        "extra": {},
    }

    result = build_dcat_dataset(str(source), cast(NormalizedMetadata, metadata))

    themes = {item["@id"] for item in result["dcat:theme"]}
    assert "theme:PopulationDistributionDemography" in themes


def test_build_dcat_dataset_infers_csv_variable_domains(tmp_path):
    source = tmp_path / "climate.csv"
    source.write_text("placeholder", encoding="utf-8")
    metadata = {
        "format": "CSV",
        "title": "Climate indicators",
        "description": "Temperature, rainfall, humidity and wind observations",
        "variables": [
            {"name": "TN", "standard_name": None, "long_name": "TN", "units": None, "shape": [], "dimensions": []},
            {"name": "RR", "standard_name": None, "long_name": "RR", "units": None, "shape": [], "dimensions": []},
            {"name": "RH_MEAN", "standard_name": None, "long_name": "RH_MEAN", "units": None, "shape": [], "dimensions": []},
            {"name": "WS_MAX", "standard_name": None, "long_name": "WS_MAX", "units": None, "shape": [], "dimensions": []},
        ],
        "extra": {},
    }

    result = build_dcat_dataset(str(source), cast(NormalizedMetadata, metadata))

    ontology_ids = {item["@id"] for item in result["cf:ontologyMappings"]}
    theme_ids = {item["@id"] for item in result["dcat:theme"]}

    assert "sweet:AirTemperature" in ontology_ids
    assert "sweet:Precipitation" in ontology_ids
    assert "sweet:RelativeHumidity" in ontology_ids
    assert "sweet:WindSpeed" in ontology_ids
    assert "theme:AtmosphericConditions" in theme_ids
    assert "theme:HydrologicalConditions" in theme_ids
