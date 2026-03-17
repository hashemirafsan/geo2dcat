from __future__ import annotations

import asyncio
import importlib
import json
from typing import Any, Dict, Iterable, List, Optional

SYSTEM_PROMPT = """You are a geospatial metadata expert specializing in DCAT 3 and CF Conventions.

Given ambiguous or incomplete technical metadata from a scientific dataset file,
produce the correct DCAT 3 JSON-LD output with proper ontology mappings.

Rules:
- Use SWEET ontology URIs for atmospheric/ocean/cryo variables
- Use ENVO ontology URIs for land/ecological variables
- Use INSPIRE themes for dcat:theme
- If standard_name cannot be determined, set cf:ontologyURI to null
- Confidence score (0.0-1.0) must be included per variable mapping
- Return ONLY valid JSON, no explanation

Output format: DCAT 3 JSON-LD as specified in the context.
"""


async def generate_claude_hard_cases(
    client: Any,
    inputs: Iterable[Dict[str, Any]],
    max_concurrent: int = 10,
) -> List[Dict[str, Any]]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _one(item: Dict[str, Any]) -> Dict[str, Any]:
        async with semaphore:
            response = await client.messages.create(
                model="claude-3-5-sonnet-latest",
                max_tokens=3000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": json.dumps(item)}],
            )
            text = getattr(response.content[0], "text", "{}")
            parsed = json.loads(text)
            return {
                "input": item,
                "output": parsed,
                "difficulty": "hard",
                "scenario": item.get("scenario", "claude_generated"),
            }

    tasks = [_one(item) for item in inputs]
    return await asyncio.gather(*tasks) if tasks else []


def build_claude_client(api_key: Optional[str]) -> Any:
    if not api_key:
        return None
    try:
        anthropic = importlib.import_module("anthropic")
    except ImportError as exc:
        raise ImportError("Anthropic support requires `pip install geo2dcat[synthetic]`.") from exc
    return anthropic.AsyncAnthropic(api_key=api_key)
