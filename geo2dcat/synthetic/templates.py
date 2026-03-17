from __future__ import annotations

from typing import Any, Dict, List


def build_template_cases() -> List[Dict[str, Any]]:
    return [
        {
            "scenario": "ambiguous_variable_names",
            "input": {
                "format": "NetCDF",
                "title": "Regional temp anomaly",
                "description": "Ambiguous temperature field without CF standard name.",
                "institution": "Example Climate Lab",
                "creator": None,
                "creator_email": None,
                "license": None,
                "references": None,
                "history": None,
                "conventions": [],
                "bbox_wkt": None,
                "time_start": None,
                "time_end": None,
                "crs": "EPSG:4326",
                "variables": [
                    {
                        "name": "temp",
                        "standard_name": None,
                        "long_name": "surface air temperature",
                        "units": "K",
                        "shape": [365, 180, 360],
                        "dimensions": ["time", "lat", "lon"],
                    }
                ],
                "extra": {},
            },
        },
        {
            "scenario": "missing_standard_name",
            "input": {
                "format": "NetCDF",
                "title": "ERA5 precipitation",
                "description": "Precipitation field without standard name.",
                "institution": "ECMWF",
                "creator": None,
                "creator_email": None,
                "license": None,
                "references": None,
                "history": None,
                "conventions": ["CF-1.7"],
                "bbox_wkt": None,
                "time_start": None,
                "time_end": None,
                "crs": "EPSG:4326",
                "variables": [
                    {
                        "name": "tp",
                        "standard_name": None,
                        "long_name": "total precipitation",
                        "units": "kg m-2 s-1",
                        "shape": [24, 181, 360],
                        "dimensions": ["time", "lat", "lon"],
                    }
                ],
                "extra": {},
            },
        },
        {
            "scenario": "description_only",
            "input": {
                "format": "CSV",
                "title": None,
                "description": "Station observations of humidity and wind speed from a coastal region.",
                "institution": "Marine Weather Office",
                "creator": None,
                "creator_email": None,
                "license": None,
                "references": None,
                "history": None,
                "conventions": [],
                "bbox_wkt": None,
                "time_start": None,
                "time_end": None,
                "crs": None,
                "variables": [
                    {
                        "name": "humidity_idx",
                        "standard_name": None,
                        "long_name": "relative humidity",
                        "units": "%",
                        "shape": [],
                        "dimensions": [],
                    },
                    {
                        "name": "gust",
                        "standard_name": None,
                        "long_name": "wind gust",
                        "units": "m s-1",
                        "shape": [],
                        "dimensions": [],
                    },
                ],
                "extra": {},
            },
        },
    ]
