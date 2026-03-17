from __future__ import annotations

import csv
from pathlib import Path

from geo2dcat.types import NormalizedMetadata
from geo2dcat.utils import empty_metadata


def _normalize_headers(headers: list[str]) -> list[str]:
    normalized = []
    used = set()
    for index, header in enumerate(headers):
        candidate = (header or "").strip()
        if not candidate or candidate.lower().startswith("unnamed:"):
            candidate = "row_id" if index == 0 else f"column_{index + 1}"
        original = candidate
        suffix = 2
        while candidate in used:
            candidate = f"{original}_{suffix}"
            suffix += 1
        used.add(candidate)
        normalized.append(candidate)
    return normalized


def extract_csv(filepath: str) -> NormalizedMetadata:
    path = Path(filepath)
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    metadata = empty_metadata("CSV")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        raw_headers = next(reader, [])
        headers = _normalize_headers(raw_headers)
        sample_rows = []
        for _, row in zip(range(5), reader):
            values = list(row)
            if len(values) < len(headers):
                values.extend([""] * (len(headers) - len(values)))
            elif len(values) > len(headers):
                values = values[: len(headers)]
            sample_rows.append(dict(zip(headers, values)))
    metadata.update(
        {
            "title": path.stem,
            "description": f"Tabular dataset with {len(headers)} columns",
            "variables": [
                {
                    "name": column,
                    "standard_name": None,
                    "long_name": column,
                    "units": None,
                    "shape": [],
                    "dimensions": [],
                }
                for column in headers
            ],
            "extra": {"delimiter": delimiter, "columns": headers, "sample_rows": sample_rows},
        }
    )
    return metadata
