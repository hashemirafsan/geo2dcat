from __future__ import annotations

from pathlib import Path

from geo2dcat.types import NormalizedMetadata
from geo2dcat.utils import bbox_to_wkt, empty_metadata, is_coordinate_variable, normalize_iso_datetime, optional_import


def extract_grib(filepath: str) -> NormalizedMetadata:
    xarray = optional_import("xarray", "pip install geo2dcat[grib]")
    optional_import("cfgrib", "pip install geo2dcat[grib]")
    path = Path(filepath)
    metadata = empty_metadata("GRIB")
    with xarray.open_dataset(path, engine="cfgrib") as dataset:
        attrs = {str(key): str(value) for key, value in dataset.attrs.items()}
        metadata.update(
            {
                "title": attrs.get("title") or path.stem,
                "description": attrs.get("GRIB_name") or attrs.get("description"),
                "institution": attrs.get("institution") or attrs.get("centre"),
                "conventions": ["CF-1.7"],
                "variables": [
                    {
                        "name": name,
                        "standard_name": getattr(data_array, "standard_name", None),
                        "long_name": getattr(data_array, "long_name", None) or data_array.attrs.get("GRIB_name"),
                        "units": data_array.attrs.get("units"),
                        "shape": [int(value) for value in data_array.shape],
                        "dimensions": [str(dim) for dim in data_array.dims],
                    }
                    for name, data_array in dataset.data_vars.items()
                    if not is_coordinate_variable(name, data_array.dims)
                ],
                "extra": attrs,
            }
        )
        if "latitude" in dataset and "longitude" in dataset:
            lat = dataset["latitude"]
            lon = dataset["longitude"]
            metadata["bbox_wkt"] = bbox_to_wkt(float(lon.min()), float(lat.min()), float(lon.max()), float(lat.max()))
        times = None
        if "time" in dataset:
            times = dataset["time"].values
        elif "valid_time" in dataset:
            times = dataset["valid_time"].values
        if times is not None and len(times):
            metadata["time_start"] = normalize_iso_datetime(times[0])
            metadata["time_end"] = normalize_iso_datetime(times[-1])
    return metadata
