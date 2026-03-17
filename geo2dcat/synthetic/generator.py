from __future__ import annotations

import asyncio
import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

from geo2dcat.dcat_builder import build_dcat_dataset
from geo2dcat.synthetic.augmentor import augment_seed_cases
from geo2dcat.synthetic.hard_cases import build_claude_client, generate_claude_hard_cases
from geo2dcat.synthetic.templates import build_template_cases
from geo2dcat.utils import ensure_parent_dir


class SyntheticGenerator:
    def __init__(self, seed_dcat_dir: str, anthropic_api_key: Optional[str] = None) -> None:
        self.seed_dcat_dir = Path(seed_dcat_dir)
        self.anthropic_api_key = anthropic_api_key

    def generate(
        self,
        augment_count: int = 0,
        template_count: int = 0,
        claude_count: int = 0,
        output_path: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        rng = random.Random(seed)
        seed_cases = self._load_seed_cases()
        template_cases = self._generate_template_cases(template_count)
        augmented = augment_seed_cases(seed_cases, augment_count, rng)
        claude_cases = self._generate_claude_cases(template_cases[:claude_count]) if claude_count > 0 else []
        dataset = augmented + template_cases + claude_cases
        if output_path:
            path = Path(output_path)
            ensure_parent_dir(path)
            with path.open("w", encoding="utf-8") as handle:
                for item in dataset:
                    handle.write(json.dumps(item, ensure_ascii=True) + "\n")
        return {
            "total": len(dataset),
            "augmented": len(augmented),
            "template": len(template_cases),
            "claude": len(claude_cases),
            "path": output_path,
        }


    def _load_seed_cases(self) -> List[Dict[str, Any]]:
        if not self.seed_dcat_dir.exists():
            return []
        cases: List[Dict[str, Any]] = []
        for path in self.seed_dcat_dir.glob("*.json*"):
            try:
                output = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            cases.append(
                {
                    "input": {
                        "format": output.get("dct:format"),
                        "title": output.get("dct:title", {}).get("@value") if isinstance(output.get("dct:title"), dict) else None,
                        "description": output.get("dct:description", {}).get("@value") if isinstance(output.get("dct:description"), dict) else None,
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
                    },
                    "output": output,
                    "scenario": "augmented_seed",
                }
            )
        return cases


    def _generate_template_cases(self, template_count: int) -> List[Dict[str, Any]]:
        if template_count <= 0:
            return []
        templates = build_template_cases()
        generated: List[Dict[str, Any]] = []
        for index in range(template_count):
            template = templates[index % len(templates)]
            normalized_input = template["input"]
            dcat_output = build_dcat_dataset(f"template_{index}.nc", normalized_input)
            generated.append(
                {
                    "input": normalized_input,
                    "output": dcat_output,
                    "difficulty": "hard",
                    "scenario": template["scenario"],
                }
            )
        return generated


    def _generate_claude_cases(self, cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        client = build_claude_client(self.anthropic_api_key)
        if client is None or not cases:
            return []
        payloads = [case["input"] | {"scenario": case["scenario"]} for case in cases]
        return asyncio.run(generate_claude_hard_cases(client, payloads, max_concurrent=10))
