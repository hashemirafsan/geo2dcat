from __future__ import annotations

import json

from geo2dcat.synthetic import SyntheticGenerator


def test_synthetic_generator_templates(tmp_path):
    seed_dir = tmp_path / "seed"
    seed_dir.mkdir()
    output = tmp_path / "training.jsonl"
    generator = SyntheticGenerator(str(seed_dir))
    summary = generator.generate(template_count=2, output_path=str(output), seed=42)
    lines = output.read_text(encoding="utf-8").strip().splitlines()
    first = json.loads(lines[0])
    assert summary["template"] == 2
    assert first["difficulty"] == "hard"
    assert "output" in first
