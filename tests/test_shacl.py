from __future__ import annotations

from geo2dcat.shacl_generator import generate_shacl


def test_generate_shacl_basic(tmp_path):
    outputs = [
        {
            "@context": {},
            "@type": "dcat:Dataset",
            "@id": "urn:dataset:a",
            "dct:title": {"@value": "A", "@language": "en"},
            "dct:format": "CSV",
            "dcat:theme": [{"@id": "theme:AtmosphericConditions"}],
            "cf:ontologyMappings": [],
            "cf:variableMappings": [],
        },
        {
            "@context": {},
            "@type": "dcat:Dataset",
            "@id": "urn:dataset:b",
            "dct:title": {"@value": "B", "@language": "en"},
            "dct:format": "CSV",
            "dcat:theme": [{"@id": "theme:HydrologicalConditions"}],
            "cf:ontologyMappings": [],
            "cf:variableMappings": [],
        },
    ]
    path = tmp_path / "shape.ttl"
    turtle = generate_shacl(outputs, shape_name="ClimateDatasetShape", output_path=str(path))
    assert "ClimateDatasetShape" in turtle
    assert "sh:minCount 1" in turtle
    assert path.exists()
