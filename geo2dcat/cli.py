from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

from geo2dcat import batch_convert, convert, convert_to_file, supported_formats
from geo2dcat.dcat_builder import DCAT_CONTEXT
from geo2dcat.mappings import CF_SHORT_ALIASES, CF_STANDARD_NAME_MAPPING
from geo2dcat.shacl_generator import generate_shacl
from geo2dcat.synthetic import SyntheticGenerator


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="geo2dcat")
    subparsers = parser.add_subparsers(dest="command")

    convert_parser = subparsers.add_parser("convert")
    convert_parser.add_argument("filepath")
    convert_parser.add_argument("--output")
    convert_parser.add_argument("--id", dest="dataset_id")
    convert_parser.add_argument("--variables-only", action="store_true")
    convert_parser.add_argument("--quiet", action="store_true")
    convert_parser.add_argument("--format", choices=["json", "turtle"], default="json")
    convert_parser.set_defaults(func=_cmd_convert)

    batch_parser = subparsers.add_parser("batch")
    batch_parser.add_argument("directory")
    batch_parser.add_argument("--pattern")
    batch_parser.add_argument("--output")
    batch_parser.add_argument("--quiet", action="store_true")
    batch_parser.set_defaults(func=_cmd_batch)

    shacl_parser = subparsers.add_parser("shacl")
    shacl_parser.add_argument("directory")
    shacl_parser.add_argument("--shape-name", default="DatasetShape")
    shacl_parser.add_argument("--output")
    shacl_parser.set_defaults(func=_cmd_shacl)

    synthetic_parser = subparsers.add_parser("synthetic")
    synthetic_parser.add_argument("--seed-dir", required=True)
    synthetic_parser.add_argument("--augment", type=int, default=0)
    synthetic_parser.add_argument("--templates", type=int, default=0)
    synthetic_parser.add_argument("--claude", type=int, default=0)
    synthetic_parser.add_argument("--output", required=True)
    synthetic_parser.add_argument("--api-key")
    synthetic_parser.set_defaults(func=_cmd_synthetic)

    formats_parser = subparsers.add_parser("formats")
    formats_parser.set_defaults(func=_cmd_formats)

    lookup_parser = subparsers.add_parser("lookup")
    lookup_parser.add_argument("name")
    lookup_parser.set_defaults(func=_cmd_lookup)

    return parser


def _cmd_convert(args: argparse.Namespace) -> int:
    result = convert(args.filepath, dataset_id=args.dataset_id)
    payload: Any = result.get("cf:variableMappings") if args.variables_only else result
    if args.output:
        convert_to_file(args.filepath, args.output, dataset_id=args.dataset_id)
        if not args.quiet:
            print(f"Saved DCAT output to {args.output}")
        return 0
    text = _serialize_output(payload, args.format)
    if not args.quiet:
        print(text)
    return 0


def _cmd_batch(args: argparse.Namespace) -> int:
    results = batch_convert(args.directory, pattern=args.pattern)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(results, indent=2, ensure_ascii=True), encoding="utf-8")
    if not args.quiet:
        print(json.dumps(results, indent=2, ensure_ascii=True))
    return 0


def _cmd_shacl(args: argparse.Namespace) -> int:
    results = batch_convert(args.directory)
    dcat_outputs = [item["dcat"] for item in results if item["status"] == "ok" and item["dcat"]]
    turtle = generate_shacl(dcat_outputs, shape_name=args.shape_name, output_path=args.output)
    if not args.output:
        print(turtle)
    else:
        print(f"Saved SHACL output to {args.output}")
    return 0


def _cmd_synthetic(args: argparse.Namespace) -> int:
    generator = SyntheticGenerator(args.seed_dir, anthropic_api_key=args.api_key or os.getenv("ANTHROPIC_API_KEY"))
    summary = generator.generate(
        augment_count=args.augment,
        template_count=args.templates,
        claude_count=args.claude,
        output_path=args.output,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


def _cmd_formats(_: argparse.Namespace) -> int:
    print(json.dumps(supported_formats(), indent=2, ensure_ascii=True))
    return 0


def _cmd_lookup(args: argparse.Namespace) -> int:
    name = args.name
    standard_name = CF_SHORT_ALIASES.get(name, name)
    ontology_uri = CF_STANDARD_NAME_MAPPING.get(standard_name) if standard_name else None
    payload = {
        "input": name,
        "cf_standard_name": standard_name if ontology_uri else None,
        "ontology_uri": ontology_uri,
        "context": DCAT_CONTEXT,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))
    return 0


def _serialize_output(payload: Any, output_format: str) -> str:
    if output_format == "json":
        return json.dumps(payload, indent=2, ensure_ascii=True)
    try:
        from rdflib import Graph  # type: ignore[import-not-found]
    except ImportError as exc:
        raise ImportError("Turtle output requires `pip install geo2dcat[rdf]`.") from exc
    graph = Graph()
    graph.parse(data=json.dumps(payload), format="json-ld")
    return str(graph.serialize(format="turtle"))


if __name__ == "__main__":
    sys.exit(main())
