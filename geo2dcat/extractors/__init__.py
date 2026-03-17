from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict

from geo2dcat.extractors.csv import extract_csv
from geo2dcat.extractors.geotiff import extract_geotiff
from geo2dcat.extractors.grib import extract_grib
from geo2dcat.extractors.hdf5 import extract_hdf5
from geo2dcat.extractors.netcdf import extract_netcdf
from geo2dcat.extractors.shapefile import extract_vector
from geo2dcat.types import NormalizedMetadata

Extractor = Callable[[str], NormalizedMetadata]

EXTRACTOR_BY_SUFFIX: Dict[str, Extractor] = {
    ".nc": extract_netcdf,
    ".nc4": extract_netcdf,
    ".netcdf": extract_netcdf,
    ".tif": extract_geotiff,
    ".tiff": extract_geotiff,
    ".img": extract_geotiff,
    ".shp": extract_vector,
    ".geojson": extract_vector,
    ".gpkg": extract_vector,
    ".grib": extract_grib,
    ".grib2": extract_grib,
    ".grb": extract_grib,
    ".grb2": extract_grib,
    ".h5": extract_hdf5,
    ".hdf5": extract_hdf5,
    ".he5": extract_hdf5,
    ".csv": extract_csv,
    ".tsv": extract_csv,
}


def extract(filepath: str) -> NormalizedMetadata:
    path = Path(filepath)
    suffix = path.suffix.lower()
    extractor = EXTRACTOR_BY_SUFFIX.get(suffix)
    if extractor is None:
        raise ValueError(f"Unsupported format: {suffix or '<none>'}")
    return extractor(str(path))


def supported_formats() -> Dict[str, str]:
    return {
        ".nc/.nc4/.netcdf": "NetCDF",
        ".tif/.tiff/.img": "GeoTIFF",
        ".shp/.geojson/.gpkg": "Shapefile / Vector",
        ".grib/.grib2/.grb/.grb2": "GRIB",
        ".h5/.hdf5/.he5": "HDF5",
        ".csv/.tsv": "CSV",
    }
