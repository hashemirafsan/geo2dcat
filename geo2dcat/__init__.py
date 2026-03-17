from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from geo2dcat.dcat_builder import build_dcat_dataset
from geo2dcat.extractors import extract, supported_formats
from geo2dcat.types import NormalizedMetadata
from geo2dcat.utils import ensure_parent_dir

__all__ = ["batch_convert", "convert", "convert_to_file", "supported_formats"]


def convert(filepath: str, dataset_id: Optional[str] = None) -> Dict[str, Any]:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(filepath)
    metadata = _safe_extract(str(path))
    return build_dcat_dataset(str(path), metadata, dataset_id=dataset_id)


def convert_to_file(filepath: str, output_path: str, dataset_id: Optional[str] = None) -> str:
    result = convert(filepath, dataset_id=dataset_id)
    path = Path(output_path)
    ensure_parent_dir(path)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=True), encoding="utf-8")
    return str(path)


def batch_convert(directory: str, pattern: Optional[str] = None) -> List[Dict[str, Any]]:
    base_dir = Path(directory)
    if not base_dir.exists():
        raise FileNotFoundError(directory)
    glob_pattern = pattern or "**/*"
    results: List[Dict[str, Any]] = []
    for path in sorted(candidate for candidate in base_dir.glob(glob_pattern) if candidate.is_file()):
        try:
            dcat = convert(str(path))
            results.append({"file": str(path), "status": "ok", "dcat": dcat, "error": None})
        except Exception as exc:
            results.append({"file": str(path), "status": "error", "dcat": None, "error": str(exc)})
    return results


def _safe_extract(filepath: str) -> NormalizedMetadata:
    try:
        return extract(filepath)
    except (ValueError, ImportError):
        raise
    except Exception as exc:
        path = Path(filepath)
        return {
            "format": path.suffix.lstrip(".") or "unknown",
            "title": path.stem,
            "description": None,
            "institution": None,
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
            "variables": [],
            "extra": {"error": str(exc)},
        }
