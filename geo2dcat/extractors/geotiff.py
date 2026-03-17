from __future__ import annotations

from pathlib import Path

from geo2dcat.types import NormalizedMetadata
from geo2dcat.utils import bbox_to_wkt, empty_metadata, optional_import


def extract_geotiff(filepath: str) -> NormalizedMetadata:
    rasterio = optional_import("rasterio", "pip install geo2dcat[geotiff]")
    path = Path(filepath)
    metadata = empty_metadata("GeoTIFF")
    with rasterio.open(path) as dataset:
        bounds = dataset.bounds
        metadata.update(
            {
                "title": path.stem,
                "description": dataset.tags().get("DESCRIPTION") or dataset.tags().get("TIFFTAG_IMAGEDESCRIPTION"),
                "crs": dataset.crs.to_string() if dataset.crs else None,
                "bbox_wkt": bbox_to_wkt(bounds.left, bounds.bottom, bounds.right, bounds.top),
                "variables": [
                    {
                        "name": f"band_{index}",
                        "standard_name": None,
                        "long_name": dataset.descriptions[index - 1] if dataset.descriptions else None,
                        "units": None,
                        "shape": [dataset.height, dataset.width],
                        "dimensions": ["y", "x"],
                    }
                    for index in range(1, dataset.count + 1)
                ],
                "extra": {
                    "count": dataset.count,
                    "driver": dataset.driver,
                    "dtype": dataset.dtypes[0] if dataset.dtypes else None,
                },
            }
        )
    return metadata
