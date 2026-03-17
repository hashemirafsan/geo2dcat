from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class VariableInfo(TypedDict, total=False):
    name: str
    standard_name: Optional[str]
    long_name: Optional[str]
    units: Optional[str]
    cf_resolved: Optional[str]
    ontology_uri: Optional[str]
    theme: Optional[str]
    shape: List[int]
    dimensions: List[str]
    confidence: Optional[float]


class NormalizedMetadata(TypedDict, total=False):
    format: str
    title: Optional[str]
    description: Optional[str]
    institution: Optional[str]
    creator: Optional[str]
    creator_email: Optional[str]
    license: Optional[str]
    references: Optional[str]
    history: Optional[str]
    conventions: List[str]
    bbox_wkt: Optional[str]
    time_start: Optional[str]
    time_end: Optional[str]
    crs: Optional[str]
    variables: List[VariableInfo]
    extra: Dict[str, Any]
