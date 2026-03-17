from __future__ import annotations

import copy
import datetime as dt
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from geo2dcat.mappings.cf_short_aliases import CF_SHORT_ALIASES
from geo2dcat.mappings.cf_standard_names import CF_STANDARD_NAME_MAPPING
from geo2dcat.mappings.themes import ONTOLOGY_KEYWORD_MAPPING, THEME_KEYWORD_MAPPING, THEME_MAPPING
from geo2dcat.types import NormalizedMetadata, VariableInfo

COORDINATE_NAMES = {
    "lat",
    "latitude",
    "lon",
    "longitude",
    "time",
    "level",
    "lev",
    "x",
    "y",
    "band",
}

LOWERCASE_CF_SHORT_ALIASES = {key.lower(): value for key, value in CF_SHORT_ALIASES.items()}


def slugify_dataset_id(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "dataset"


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_iso_datetime(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, dt.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=dt.timezone.utc)
        return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    text = str(value).strip()
    if not text:
        return None
    text = text.replace(" ", "T")
    if text.endswith("Z"):
        return text
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return text
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_json_dump(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=True)


def infer_license_identifier(value: Optional[str]) -> Optional[Any]:
    if not value:
        return None
    license_text = value.strip()
    lower = license_text.lower()
    if lower.startswith("http://") or lower.startswith("https://"):
        return {"@id": license_text}
    known = {
        "cc-by-4.0": "https://creativecommons.org/licenses/by/4.0/",
        "cc by 4.0": "https://creativecommons.org/licenses/by/4.0/",
        "mit": "https://opensource.org/license/mit/",
    }
    if lower in known:
        return {"@id": known[lower]}
    return {"@value": license_text}


def empty_metadata(format_name: str) -> NormalizedMetadata:
    return {
        "format": format_name,
        "title": None,
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
        "extra": {},
    }


def is_coordinate_variable(name: str, dimensions: Optional[Sequence[str]] = None) -> bool:
    lowered = name.lower()
    if lowered in COORDINATE_NAMES:
        return True
    dims = [dim.lower() for dim in (dimensions or [])]
    return lowered in dims and lowered in {"time", "lat", "latitude", "lon", "longitude", "x", "y"}


def resolve_variable_mapping(variable: VariableInfo) -> VariableInfo:
    resolved = copy.deepcopy(variable)
    raw_name = (resolved.get("name") or "").strip()
    standard_name = resolved.get("standard_name")
    long_name = resolved.get("long_name")

    cf_name = standard_name or None
    if not cf_name and raw_name:
        cf_name = CF_SHORT_ALIASES.get(raw_name)
    if not cf_name and raw_name.lower() in CF_SHORT_ALIASES:
        cf_name = CF_SHORT_ALIASES.get(raw_name.lower())
    if not cf_name and raw_name:
        cf_name = LOWERCASE_CF_SHORT_ALIASES.get(raw_name.lower())
    if not cf_name and long_name:
        normalized_long_name = long_name.strip().lower().replace(" ", "_")
        cf_name = CF_STANDARD_NAME_MAPPING.get(normalized_long_name) and normalized_long_name
    ontology_uri = CF_STANDARD_NAME_MAPPING.get(cf_name) if cf_name else None
    theme = THEME_MAPPING.get(ontology_uri) if ontology_uri else None

    resolved["cf_resolved"] = cf_name
    resolved["ontology_uri"] = ontology_uri
    resolved["theme"] = theme
    resolved.setdefault("shape", [])
    resolved.setdefault("dimensions", [])
    return resolved


def collect_themes(
    variables: Iterable[VariableInfo],
    metadata: Optional[NormalizedMetadata] = None,
    source_path: Optional[Path] = None,
) -> List[str]:
    values = {str(var.get("theme")) for var in variables if var.get("theme")}
    for ontology_uri in infer_ontology_keywords(metadata, source_path=source_path, variables=variables):
        theme = THEME_MAPPING.get(ontology_uri)
        if theme:
            values.add(theme)
    for theme in infer_theme_keywords(metadata, source_path=source_path, variables=variables):
        values.add(theme)
    return sorted(theme for theme in values if theme)


def collect_ontology_uris(
    variables: Iterable[VariableInfo],
    metadata: Optional[NormalizedMetadata] = None,
    source_path: Optional[Path] = None,
) -> List[str]:
    values = {str(var.get("ontology_uri")) for var in variables if var.get("ontology_uri")}
    values.update(infer_ontology_keywords(metadata, source_path=source_path, variables=variables))
    return sorted(uri for uri in values if uri)


def infer_theme_keywords(
    metadata: Optional[NormalizedMetadata],
    source_path: Optional[Path] = None,
    variables: Optional[Iterable[VariableInfo]] = None,
) -> List[str]:
    text = _semantic_text(metadata, source_path=source_path, variables=variables)
    return _keyword_matches(text, THEME_KEYWORD_MAPPING)


def infer_ontology_keywords(
    metadata: Optional[NormalizedMetadata],
    source_path: Optional[Path] = None,
    variables: Optional[Iterable[VariableInfo]] = None,
) -> List[str]:
    text = _semantic_text(metadata, source_path=source_path, variables=variables)
    return _keyword_matches(text, ONTOLOGY_KEYWORD_MAPPING)


def _semantic_text(
    metadata: Optional[NormalizedMetadata],
    source_path: Optional[Path] = None,
    variables: Optional[Iterable[VariableInfo]] = None,
) -> str:
    parts: List[str] = []
    if source_path:
        parts.extend([source_path.stem, source_path.name])
    if metadata:
        parts.extend(
            [
                str(metadata.get("title") or ""),
                str(metadata.get("description") or ""),
                str(metadata.get("format") or ""),
            ]
        )
        extra = metadata.get("extra") or {}
        if isinstance(extra, dict):
            columns = extra.get("columns")
            if isinstance(columns, list):
                parts.extend(str(item) for item in columns)
    for variable in variables or []:
        parts.extend(
            [
                str(variable.get("name") or ""),
                str(variable.get("standard_name") or ""),
                str(variable.get("long_name") or ""),
                str(variable.get("cf_resolved") or ""),
            ]
        )
    combined = " ".join(parts).lower()
    return combined.replace("_", " ").replace("-", " ")


def _keyword_matches(text: str, mapping: Dict[str, str]) -> List[str]:
    matches = {value for keyword, value in mapping.items() if keyword in text}
    return sorted(matches)


def file_modified_iso(path: Path) -> str:
    stamp = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc)
    return stamp.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def bbox_to_wkt(minx: float, miny: float, maxx: float, maxy: float) -> str:
    values = [minx, miny, maxx, maxy]
    cleaned = [0.0 if math.isnan(v) else v for v in values]
    minx, miny, maxx, maxy = cleaned
    return (
        f"POLYGON(({minx} {miny}, {maxx} {miny}, {maxx} {maxy}, "
        f"{minx} {maxy}, {minx} {miny}))"
    )


def best_effort_title(path: Path, metadata: NormalizedMetadata) -> str:
    return metadata.get("title") or path.stem.replace("_", " ").replace("-", " ").strip() or path.name


def simplify_value(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return str(value)
    if isinstance(value, (list, tuple)):
        return [simplify_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): simplify_value(v) for k, v in value.items()}
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    return value


def optional_import(package_name: str, install_hint: str):
    try:
        return __import__(package_name)
    except ImportError as exc:
        raise ImportError(f"Missing optional dependency '{package_name}'. Install with `{install_hint}`.") from exc


def normalize_conventions(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value)
    separators = [",", ";"]
    for sep in separators:
        if sep in text:
            return [item.strip() for item in text.split(sep) if item.strip()]
    return [text.strip()] if text.strip() else []


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def summarize_variables(variables: Sequence[VariableInfo]) -> Dict[str, Any]:
    return {
        "count": len(variables),
        "names": [var.get("name") for var in variables],
    }
