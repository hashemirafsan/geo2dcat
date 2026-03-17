from __future__ import annotations

from pathlib import Path
from typing import Any, List

from geo2dcat.types import NormalizedMetadata, VariableInfo
from geo2dcat.utils import (
    bbox_to_wkt,
    empty_metadata,
    is_coordinate_variable,
    normalize_conventions,
    normalize_iso_datetime,
    optional_import,
    simplify_value,
)


def extract_netcdf(filepath: str) -> NormalizedMetadata:
    netcdf4 = optional_import("netCDF4", "pip install geo2dcat[netcdf]")
    path = Path(filepath)
    metadata = empty_metadata("NetCDF")
    with netcdf4.Dataset(path, mode="r") as dataset:
        attrs = {name: simplify_value(dataset.getncattr(name)) for name in dataset.ncattrs()}
        metadata.update(
            {
                "title": _pick(attrs, ["title", "dataset_title"]),
                "description": _pick(attrs, ["summary", "description", "comment"]),
                "institution": _pick(attrs, ["institution", "publisher_name"]),
                "creator": _pick(attrs, ["creator_name", "author", "creator"]),
                "creator_email": _pick(attrs, ["creator_email", "author_email"]),
                "license": _pick(attrs, ["license"]),
                "references": _pick(attrs, ["references"]),
                "history": _pick(attrs, ["history"]),
                "conventions": normalize_conventions(_pick(attrs, ["Conventions", "conventions"])),
                "crs": _detect_crs(dataset),
                "extra": {"global_attributes": attrs},
            }
        )
        metadata["bbox_wkt"] = _detect_bbox(dataset, attrs)
        time_start, time_end = _detect_time_range(dataset)
        metadata["time_start"] = time_start
        metadata["time_end"] = time_end
        metadata["variables"] = _extract_variables(dataset.variables)
    return metadata


def _extract_variables(variables: Any) -> List[VariableInfo]:
    items: List[VariableInfo] = []
    for name, variable in variables.items():
        dimensions = list(getattr(variable, "dimensions", ()))
        if is_coordinate_variable(name, dimensions):
            continue
        items.append(
            {
                "name": name,
                "standard_name": getattr(variable, "standard_name", None),
                "long_name": getattr(variable, "long_name", None),
                "units": getattr(variable, "units", None),
                "shape": [int(value) for value in getattr(variable, "shape", ())],
                "dimensions": [str(item) for item in dimensions],
            }
        )
    return items


def _pick(attrs: dict, keys: List[str]):
    for key in keys:
        if key in attrs and attrs[key] not in (None, ""):
            return str(attrs[key])
    return None


def _detect_crs(dataset: Any):
    for candidate in ["crs", "spatial_ref"]:
        if candidate in dataset.variables:
            var = dataset.variables[candidate]
            for attr in ["epsg_code", "spatial_ref", "crs_wkt"]:
                if hasattr(var, attr):
                    return str(getattr(var, attr))
    return None


def _detect_bbox(dataset: Any, attrs: dict):
    lat = _read_coordinate(dataset, ["lat", "latitude", "y"])
    lon = _read_coordinate(dataset, ["lon", "longitude", "x"])
    if lat is not None and lon is not None and len(lat) and len(lon):
        return bbox_to_wkt(float(min(lon)), float(min(lat)), float(max(lon)), float(max(lat)))
    lat_min = attrs.get("geospatial_lat_min")
    lat_max = attrs.get("geospatial_lat_max")
    lon_min = attrs.get("geospatial_lon_min")
    lon_max = attrs.get("geospatial_lon_max")
    if None not in (lat_min, lat_max, lon_min, lon_max):
        return bbox_to_wkt(
            float(str(lon_min)),
            float(str(lat_min)),
            float(str(lon_max)),
            float(str(lat_max)),
        )
    return None


def _read_coordinate(dataset: Any, names: List[str]):
    for name in names:
        if name in dataset.variables:
            variable = dataset.variables[name]
            try:
                data = variable[:]
            except Exception:
                return None
            flattened = getattr(data, "compressed", lambda: data)()
            try:
                return flattened.tolist()
            except Exception:
                return list(flattened)
    return None


def _detect_time_range(dataset: Any):
    if "time" not in dataset.variables:
        return None, None
    variable = dataset.variables["time"]
    try:
        values = variable[:]
    except Exception:
        return None, None
    try:
        converted = optional_import("netCDF4", "pip install geo2dcat[netcdf]").num2date(
            values,
            getattr(variable, "units", None),
            getattr(variable, "calendar", "standard"),
        )
    except Exception:
        return None, None
    sequence = list(converted)
    if not sequence:
        return None, None
    return normalize_iso_datetime(sequence[0]), normalize_iso_datetime(sequence[-1])
