from __future__ import annotations

from pathlib import Path

from geo2dcat.types import NormalizedMetadata
from geo2dcat.utils import bbox_to_wkt, empty_metadata, optional_import


def extract_vector(filepath: str) -> NormalizedMetadata:
    geopandas = optional_import("geopandas", "pip install geo2dcat[shapefile]")
    path = Path(filepath)
    metadata = empty_metadata("Shapefile")
    gdf = geopandas.read_file(path, rows=1)
    minx, miny, maxx, maxy = gdf.total_bounds
    attribute_columns = [column for column in gdf.columns if column != gdf.geometry.name]
    metadata.update(
        {
            "title": path.stem,
            "description": f"Vector dataset with {len(attribute_columns)} attributes",
            "crs": gdf.crs.to_string() if gdf.crs else None,
            "bbox_wkt": bbox_to_wkt(float(minx), float(miny), float(maxx), float(maxy)),
            "variables": [
                {
                    "name": column,
                    "standard_name": None,
                    "long_name": column,
                    "units": None,
                    "shape": [],
                    "dimensions": [],
                }
                for column in attribute_columns
            ],
            "extra": {
                "geometry_type": str(gdf.geom_type.iloc[0]) if not gdf.empty else None,
                "columns": attribute_columns,
            },
        }
    )
    return metadata
