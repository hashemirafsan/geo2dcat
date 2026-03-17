from __future__ import annotations

from pathlib import Path
from typing import Any, List

from geo2dcat.types import NormalizedMetadata, VariableInfo
from geo2dcat.utils import empty_metadata, optional_import, simplify_value


def extract_hdf5(filepath: str) -> NormalizedMetadata:
    h5py = optional_import("h5py", "pip install geo2dcat[hdf5]")
    path = Path(filepath)
    metadata = empty_metadata("HDF5")
    variables: List[VariableInfo] = []
    with h5py.File(path, "r") as handle:
        attrs = {str(key): simplify_value(value) for key, value in handle.attrs.items()}
        handle.visititems(lambda name, obj: _collect_dataset(name, obj, variables))
        metadata.update(
            {
                "title": attrs.get("title") or path.stem,
                "description": attrs.get("description") or attrs.get("summary"),
                "institution": attrs.get("institution"),
                "creator": attrs.get("creator"),
                "license": attrs.get("license"),
                "variables": variables,
                "extra": {"root_attributes": attrs},
            }
        )
    return metadata


def _collect_dataset(name: str, obj: Any, variables: List[VariableInfo]) -> None:
    if not hasattr(obj, "shape"):
        return
    variables.append(
        {
            "name": name,
            "standard_name": obj.attrs.get("standard_name"),
            "long_name": obj.attrs.get("long_name"),
            "units": obj.attrs.get("units"),
            "shape": [int(value) for value in obj.shape],
            "dimensions": [f"dim_{index}" for index, _ in enumerate(obj.shape)],
        }
    )
