from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set

from geo2dcat.utils import ensure_parent_dir

PREFIXES = {
    "": "http://example.org/shapes#",
    "sh": "http://www.w3.org/ns/shacl#",
    "dcat": "http://www.w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "geo": "http://www.opengis.net/ont/geosparql#",
    "theme": "http://inspire.ec.europa.eu/theme/",
}


def generate_shacl(
    dcat_outputs: List[Dict[str, Any]],
    shape_name: str = "DatasetShape",
    output_path: Optional[str] = None,
) -> str:
    if not dcat_outputs:
        raise ValueError("dcat_outputs cannot be empty")

    property_names = sorted(_collect_property_keys(dcat_outputs))
    total = len(dcat_outputs)
    themes = sorted(_collect_themes(dcat_outputs))

    lines = [
        '@prefix : <http://example.org/shapes#> .',
        '@prefix sh: <http://www.w3.org/ns/shacl#> .',
        '@prefix dcat: <http://www.w3.org/ns/dcat#> .',
        '@prefix dct: <http://purl.org/dc/terms/> .',
        '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .',
        '@prefix geo: <http://www.opengis.net/ont/geosparql#> .',
        '@prefix theme: <http://inspire.ec.europa.eu/theme/> .',
        '',
        f':{shape_name}',
        '    a sh:NodeShape ;',
        '    sh:targetClass dcat:Dataset ;',
    ]

    property_blocks = []
    for property_name in property_names:
        present = sum(1 for item in dcat_outputs if property_name in item)
        min_count = 1 if (present / total) >= 0.95 else 0
        datatype = _infer_datatype(next((item[property_name] for item in dcat_outputs if property_name in item), None))
        block = [
            '    sh:property [',
            f'        sh:path {property_name} ;',
            f'        sh:minCount {min_count} ;',
        ]
        if datatype:
            block.append(f'        sh:datatype {datatype} ;')
        if property_name == 'dcat:theme' and themes:
            block.append('        sh:in (')
            for theme in themes:
                block.append(f'            {theme}')
            block.append('        ) ;')
        block.append('    ]')
        property_blocks.append(block)

    for index, block in enumerate(property_blocks):
        suffix = ' ;' if index < len(property_blocks) - 1 else ' .'
        lines.extend(block[:-1])
        lines.append(block[-1] + suffix)

    turtle = "\n".join(lines) + "\n"
    if output_path:
        path = Path(output_path)
        ensure_parent_dir(path)
        path.write_text(turtle, encoding="utf-8")
    return turtle


def _collect_property_keys(dcat_outputs: Iterable[Dict[str, Any]]) -> Set[str]:
    keys: Set[str] = set()
    for item in dcat_outputs:
        keys.update(item.keys())
    keys.discard("@context")
    keys.discard("@id")
    keys.discard("@type")
    return keys


def _collect_themes(dcat_outputs: Iterable[Dict[str, Any]]) -> Set[str]:
    themes: Set[str] = set()
    for item in dcat_outputs:
        for theme in item.get("dcat:theme", []):
            if isinstance(theme, dict) and theme.get("@id"):
                themes.add(str(theme["@id"]))
    return themes


def _infer_datatype(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bool):
        return "xsd:boolean"
    if isinstance(value, int):
        return "xsd:integer"
    if isinstance(value, float):
        return "xsd:decimal"
    if isinstance(value, str):
        if value.startswith("POLYGON("):
            return "geo:wktLiteral"
        if "T" in value and value.endswith("Z"):
            return "xsd:dateTime"
        return "xsd:string"
    if isinstance(value, dict):
        if value.get("@type") == "geo:wktLiteral":
            return "geo:wktLiteral"
        if value.get("@type") == "xsd:dateTime":
            return "xsd:dateTime"
    return None
