from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from geo2dcat.types import NormalizedMetadata
from geo2dcat.utils import (
    best_effort_title,
    collect_ontology_uris,
    collect_themes,
    file_modified_iso,
    infer_license_identifier,
    resolve_variable_mapping,
    slugify_dataset_id,
    utc_now_iso,
)

DCAT_CONTEXT = {
    "dcat": "http://www.w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "prov": "http://www.w3.org/ns/prov#",
    "geo": "http://www.opengis.net/ont/geosparql#",
    "sweet": "http://sweetontology.net/repr#",
    "envo": "http://purl.obolibrary.org/obo/ENVO_",
    "theme": "http://inspire.ec.europa.eu/theme/",
    "cf": "http://cfconventions.org/cf-conventions/",
}


def build_dcat_dataset(
    source_path: str,
    metadata: NormalizedMetadata,
    dataset_id: Optional[str] = None,
) -> Dict[str, Any]:
    path = Path(source_path)
    variables = [resolve_variable_mapping(variable) for variable in metadata.get("variables", [])]
    themes = collect_themes(variables, metadata=metadata, source_path=path)
    ontology_uris = collect_ontology_uris(variables, metadata=metadata, source_path=path)
    identifier = dataset_id or f"urn:dataset:{slugify_dataset_id(path.stem)}"

    dataset: Dict[str, Any] = {
        "@context": DCAT_CONTEXT,
        "@type": "dcat:Dataset",
        "@id": identifier,
        "dct:title": {"@value": best_effort_title(path, metadata), "@language": "en"},
        "dct:format": metadata.get("format") or path.suffix.lstrip(".") or "unknown",
        "dct:modified": file_modified_iso(path) if path.exists() else utc_now_iso(),
        "dcat:theme": [{"@id": theme} for theme in themes],
        "cf:ontologyMappings": [{"@id": uri} for uri in ontology_uris],
        "cf:variableMappings": [_build_variable_mapping(variable) for variable in variables],
    }

    description = metadata.get("description")
    institution = metadata.get("institution")
    creator_name = metadata.get("creator")
    creator_email = metadata.get("creator_email")
    bbox_wkt = metadata.get("bbox_wkt")
    crs = metadata.get("crs")
    time_start = metadata.get("time_start")
    time_end = metadata.get("time_end")
    conventions = metadata.get("conventions") or []
    references = metadata.get("references")
    history = metadata.get("history")
    extra = metadata.get("extra")

    if description:
        dataset["dct:description"] = {"@value": description, "@language": "en"}
    if institution:
        dataset["dct:publisher"] = {"@type": "foaf:Organization", "foaf:name": institution}
    if creator_name:
        creator = {"@type": "foaf:Person", "foaf:name": creator_name}
        if creator_email:
            creator["foaf:mbox"] = f"mailto:{creator_email}"
        dataset["dct:creator"] = creator
    if bbox_wkt:
        spatial: Dict[str, Any] = {
            "@type": "dct:Location",
            "geo:asWKT": {"@type": "geo:wktLiteral", "@value": bbox_wkt},
        }
        if crs:
            spatial["dct:conformsTo"] = crs
        dataset["dct:spatial"] = spatial
    if time_start or time_end:
        temporal: Dict[str, Any] = {"@type": "dct:PeriodOfTime"}
        if time_start:
            temporal["dcat:startDate"] = {"@type": "xsd:dateTime", "@value": time_start}
        if time_end:
            temporal["dcat:endDate"] = {"@type": "xsd:dateTime", "@value": time_end}
        dataset["dct:temporal"] = temporal
    if conventions:
        dataset["dct:conformsTo"] = [{"@id": f"cf:{item}"} for item in conventions]
    license_identifier = infer_license_identifier(metadata.get("license"))
    if license_identifier:
        dataset["dct:license"] = license_identifier
    if references:
        dataset["dct:references"] = references
    if history:
        dataset["prov:wasGeneratedBy"] = {
            "@type": "prov:Activity",
            "prov:description": history,
        }
    if extra:
        dataset["dcat:extras"] = extra

    return {key: value for key, value in dataset.items() if value is not None}


def _build_variable_mapping(variable: Mapping[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "cf:variableName": variable.get("name"),
        "cf:standardName": variable.get("cf_resolved") or variable.get("standard_name"),
        "cf:longName": variable.get("long_name"),
        "cf:units": variable.get("units"),
        "cf:ontologyURI": variable.get("ontology_uri"),
        "cf:dimensions": variable.get("dimensions", []),
        "cf:shape": variable.get("shape", []),
    }
    if variable.get("confidence") is not None:
        payload["cf:confidence"] = variable["confidence"]
    return payload
