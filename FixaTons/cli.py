"""Command-line utilities for dataset inspection and maintenance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import COLLECTION_PATH
from .dataset_utils import (
    generate_collection_metadata,
    generate_dataset_manifest,
    generate_checksums,
    inspect_dataset,
    validate_dataset_structure,
    verify_checksums,
)


def _dataset_path(path_arg: str | None) -> Path:
    if path_arg:
        return Path(path_arg).expanduser().resolve()
    return COLLECTION_PATH.resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fixatons-datasets")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect one dataset")
    inspect_parser.add_argument("dataset", help="Path to a dataset directory")

    validate_parser = subparsers.add_parser("validate", help="Validate one dataset")
    validate_parser.add_argument("dataset", help="Path to a dataset directory")

    generate_parser = subparsers.add_parser(
        "generate", help="Generate metadata, manifests, and checksums for a collection"
    )
    generate_parser.add_argument(
        "--collection",
        help="Collection root path. Defaults to the configured dataset collection path.",
    )

    manifest_parser = subparsers.add_parser(
        "manifest", help="Generate a manifest and checksums for one dataset"
    )
    manifest_parser.add_argument("dataset", help="Path to a dataset directory")

    verify_parser = subparsers.add_parser(
        "verify-checksums", help="Verify checksums for one dataset"
    )
    verify_parser.add_argument("dataset", help="Path to a dataset directory")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "inspect":
        print(json.dumps(inspect_dataset(Path(args.dataset)), indent=2, sort_keys=True))
        return 0

    if args.command == "validate":
        validation = validate_dataset_structure(Path(args.dataset))
        print(json.dumps(validation, indent=2, sort_keys=True))
        return 0 if validation["complete_pairings"] else 1

    if args.command == "generate":
        generated = generate_collection_metadata(_dataset_path(args.collection))
        for path in generated:
            print(path)
        return 0

    if args.command == "manifest":
        dataset_path = Path(args.dataset)
        manifest_path = generate_dataset_manifest(dataset_path)
        generate_checksums(dataset_path)
        print(manifest_path)
        print(dataset_path / "checksums.md5")
        return 0

    if args.command == "verify-checksums":
        failures = verify_checksums(Path(args.dataset))
        if failures:
            print(json.dumps(failures, indent=2))
            return 1
        print("ok")
        return 0

    parser.error("Unknown command")
    return 2
