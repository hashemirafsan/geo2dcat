from __future__ import annotations

import copy
import random
from typing import Any, Dict, Iterable, List


def augment_seed_cases(seed_cases: Iterable[Dict[str, Any]], count: int, rng: random.Random) -> List[Dict[str, Any]]:
    seed_cases = list(seed_cases)
    if not seed_cases or count <= 0:
        return []
    augmented = []
    for index in range(count):
        template = copy.deepcopy(seed_cases[index % len(seed_cases)])
        output = template.get("output", {})
        title = output.get("dct:title", {}).get("@value") if isinstance(output.get("dct:title"), dict) else None
        if title:
            output["dct:title"]["@value"] = f"{title} variation {rng.randint(1000, 9999)}"
        augmented.append(
            {
                "input": template.get("input", {}),
                "output": output,
                "difficulty": "hard",
                "scenario": template.get("scenario", "augmented"),
            }
        )
    return augmented
