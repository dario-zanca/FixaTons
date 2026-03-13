"""Dataset structure utilities for FixaTons."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path


def _dataset_dirs(dataset_path: Path) -> dict[str, Path]:
    return {
        "stimuli": dataset_path / "STIMULI" if (dataset_path / "STIMULI").exists() else dataset_path / "stimuli",
        "scanpaths": dataset_path / "SCANPATHS" if (dataset_path / "SCANPATHS").exists() else dataset_path / "scanpaths",
        "fixation_maps": dataset_path / "FIXATION_MAPS" if (dataset_path / "FIXATION_MAPS").exists() else dataset_path / "fixation_maps",
        "saliency_maps": dataset_path / "SALIENCY_MAPS" if (dataset_path / "SALIENCY_MAPS").exists() else dataset_path / "saliency_maps",
    }


def _visible_files(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted([p for p in path.iterdir() if p.is_file() and not p.name.startswith(".")])


def _visible_dirs(path: Path) -> list[Path]:
    if not path.exists():
        return []
    return sorted([p for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")])


def _saliency_stem_candidates(dataset_name: str, stimulus_stem: str) -> list[str]:
    candidates = [stimulus_stem]
    if dataset_name.upper() == "TORONTO":
        candidates.append(f"d{stimulus_stem}")
    return candidates


def _resolve_matching_file(files: list[Path], dataset_name: str, stimulus_stem: str) -> Path | None:
    file_map = {file_path.stem: file_path for file_path in files}
    for candidate in _saliency_stem_candidates(dataset_name, stimulus_stem):
        if candidate in file_map:
            return file_map[candidate]
    return None


def inspect_dataset(dataset_path: Path) -> dict:
    """Return a structured summary of a dataset on disk."""
    dirs = _dataset_dirs(dataset_path)
    stimuli_files = _visible_files(dirs["stimuli"])
    fixation_files = _visible_files(dirs["fixation_maps"])
    saliency_files = _visible_files(dirs["saliency_maps"])
    scanpath_dirs = _visible_dirs(dirs["scanpaths"])

    hidden_files = sorted(
        [
            str(path.relative_to(dataset_path))
            for path in dataset_path.rglob(".*")
            if path.name not in {".", ".."} and path.name.startswith(".")
        ]
    )

    fixation_map_index = {file_path.stem: file_path for file_path in fixation_files}
    saliency_file_map = {file_path.stem: file_path for file_path in saliency_files}

    rows = []
    empty_scanpaths = []
    subject_counts = []

    for stimulus_file in stimuli_files:
        stimulus_stem = stimulus_file.stem
        scanpath_dir = dirs["scanpaths"] / stimulus_stem
        subject_files = _visible_files(scanpath_dir) if scanpath_dir.exists() else []
        subject_count = len(subject_files)
        subject_counts.append(subject_count)

        empty_subjects = [subject_file.name for subject_file in subject_files if subject_file.stat().st_size == 0]
        empty_scanpaths.extend(
            [str((scanpath_dir / subject_name).relative_to(dataset_path)) for subject_name in empty_subjects]
        )

        fixation_file = fixation_map_index.get(stimulus_stem)
        saliency_file = _resolve_matching_file(saliency_files, dataset_path.name, stimulus_stem)
        saliency_mapping_rule = "direct"
        if saliency_file is not None and saliency_file.stem != stimulus_stem:
            saliency_mapping_rule = "prefixed_with_d"

        rows.append(
            {
                "stimulus_id": stimulus_stem,
                "stimulus_file": stimulus_file.name,
                "fixation_map_file": fixation_file.name if fixation_file else "",
                "saliency_map_file": saliency_file.name if saliency_file else "",
                "scanpath_dir": scanpath_dir.name if scanpath_dir.exists() else "",
                "subject_count": subject_count,
                "empty_scanpath_files": len(empty_subjects),
                "is_complete": bool(fixation_file and saliency_file and scanpath_dir.exists()),
                "saliency_mapping_rule": saliency_mapping_rule,
            }
        )

    stimulus_stems = {file_path.stem for file_path in stimuli_files}
    fixation_stems = set(fixation_map_index)
    saliency_stems_normalized = set()
    for stem in saliency_file_map:
        if dataset_path.name.upper() == "TORONTO" and stem.startswith("d"):
            saliency_stems_normalized.add(stem[1:])
        else:
            saliency_stems_normalized.add(stem)
    scanpath_stems = {dir_path.name for dir_path in scanpath_dirs}

    return {
        "dataset_name": dataset_path.name,
        "stimuli_count": len(stimuli_files),
        "scanpath_dir_count": len(scanpath_dirs),
        "fixation_map_count": len(fixation_files),
        "saliency_map_count": len(saliency_files),
        "stimuli_extensions": sorted({file_path.suffix.lower() for file_path in stimuli_files}),
        "fixation_map_extensions": sorted({file_path.suffix.lower() for file_path in fixation_files}),
        "saliency_map_extensions": sorted({file_path.suffix.lower() for file_path in saliency_files}),
        "subject_count_min": min(subject_counts) if subject_counts else 0,
        "subject_count_max": max(subject_counts) if subject_counts else 0,
        "subject_count_unique": sorted(set(subject_counts)),
        "hidden_files": hidden_files,
        "empty_scanpaths": empty_scanpaths,
        "mismatches": {
            "missing_fixation_maps": sorted(stimulus_stems - fixation_stems),
            "missing_saliency_maps": sorted(stimulus_stems - saliency_stems_normalized),
            "missing_scanpath_dirs": sorted(stimulus_stems - scanpath_stems),
            "orphan_fixation_maps": sorted(fixation_stems - stimulus_stems),
            "orphan_saliency_maps": sorted(saliency_stems_normalized - stimulus_stems),
            "orphan_scanpath_dirs": sorted(scanpath_stems - stimulus_stems),
        },
        "rows": rows,
    }


def validate_dataset_structure(dataset_path: Path) -> dict[str, bool]:
    """Validate a dataset structure and pairing completeness."""
    summary = inspect_dataset(dataset_path)
    results = {
        "has_metadata": (dataset_path / "metadata.json").exists(),
        "has_readme": (dataset_path / "README.md").exists(),
        "has_checksums": (dataset_path / "checksums.md5").exists(),
        "stimuli_exist": summary["stimuli_count"] > 0,
        "scanpaths_exist": summary["scanpath_dir_count"] > 0,
        "fixation_maps_exist": summary["fixation_map_count"] > 0,
        "saliency_maps_exist": summary["saliency_map_count"] > 0,
        "naming_consistent": True,
        "complete_pairings": all(not values for values in summary["mismatches"].values()),
        "has_hidden_files": len(summary["hidden_files"]) > 0,
        "has_empty_scanpaths": len(summary["empty_scanpaths"]) > 0,
    }

    rows = summary["rows"]
    if rows:
        results["naming_consistent"] = all(row["scanpath_dir"] == row["stimulus_id"] for row in rows)

    return results


def create_dataset_metadata(
    dataset_path: Path,
    name: str,
    description: str,
    authors: list[str],
    year: int,
    **kwargs,
) -> None:
    """Create a metadata file for a dataset."""
    metadata = {
        "name": name,
        "version": "1.0.0",
        "description": description,
        "authors": authors,
        "year": year,
        "scanpath_format": "x_pixel y_pixel start_time end_time",
        "time_unit": "seconds",
        **kwargs,
    }

    with open(dataset_path / "metadata.json", "w", encoding="utf-8") as file_handle:
        json.dump(metadata, file_handle, indent=2, sort_keys=True)


def generate_dataset_manifest(dataset_path: Path) -> Path:
    """Generate a per-stimulus manifest for a dataset."""
    summary = inspect_dataset(dataset_path)
    manifest_path = dataset_path / "manifest.csv"

    with open(manifest_path, "w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=[
                "stimulus_id",
                "stimulus_file",
                "fixation_map_file",
                "saliency_map_file",
                "scanpath_dir",
                "subject_count",
                "empty_scanpath_files",
                "is_complete",
                "saliency_mapping_rule",
            ],
        )
        writer.writeheader()
        writer.writerows(summary["rows"])

    return manifest_path


def generate_checksums(dataset_path: Path) -> None:
    """Generate MD5 checksums for all dataset files."""
    checksums: dict[str, str] = {}

    for file_path in dataset_path.rglob("*"):
        if file_path.is_file() and file_path.name != "checksums.md5" and not file_path.name.startswith("."):
            with open(file_path, "rb") as file_handle:
                checksums[str(file_path.relative_to(dataset_path))] = hashlib.md5(
                    file_handle.read()
                ).hexdigest()

    with open(dataset_path / "checksums.md5", "w", encoding="utf-8") as file_handle:
        for file_path, checksum in sorted(checksums.items()):
            file_handle.write(f"{checksum}  {file_path}\n")


def verify_checksums(dataset_path: Path) -> list[str]:
    """Verify checksums for dataset files."""
    checksums_path = dataset_path / "checksums.md5"
    if not checksums_path.exists():
        return ["checksums.md5 not found"]

    failed_files: list[str] = []
    with open(checksums_path, "r", encoding="utf-8") as file_handle:
        for line in file_handle:
            if not line.strip():
                continue

            expected_checksum, relative_path = line.strip().split("  ", 1)
            file_path = dataset_path / relative_path
            if not file_path.exists():
                failed_files.append(f"{relative_path} (missing)")
                continue

            with open(file_path, "rb") as data_handle:
                actual_checksum = hashlib.md5(data_handle.read()).hexdigest()
            if actual_checksum != expected_checksum:
                failed_files.append(relative_path)

    return failed_files


def migrate_legacy_structure(legacy_path: Path, new_path: Path) -> None:
    """Migrate a legacy dataset tree to the normalized lowercase layout."""
    new_path.mkdir(parents=True, exist_ok=True)
    (new_path / "stimuli").mkdir(exist_ok=True)
    (new_path / "scanpaths").mkdir(exist_ok=True)
    (new_path / "fixation_maps").mkdir(exist_ok=True)
    (new_path / "saliency_maps").mkdir(exist_ok=True)

    stimuli_dir = legacy_path / "STIMULI"
    if stimuli_dir.exists():
        for index, stimulus_file in enumerate(sorted(stimuli_dir.glob("*")), start=1):
            if stimulus_file.name.startswith("."):
                continue
            new_name = f"image_{index:03d}{stimulus_file.suffix.lower()}"
            shutil.copy2(stimulus_file, new_path / "stimuli" / new_name)

    scanpaths_dir = legacy_path / "SCANPATHS"
    if scanpaths_dir.exists():
        for image_dir in sorted(scanpaths_dir.glob("*")):
            if not image_dir.is_dir() or image_dir.name.startswith("."):
                continue
            image_id = image_dir.name
            for subject_file in sorted(image_dir.glob("*")):
                if subject_file.is_file() and not subject_file.name.startswith("."):
                    new_name = f"{image_id}_subject_{subject_file.name}"
                    shutil.copy2(subject_file, new_path / "scanpaths" / new_name)

    for legacy_name, normalized_name in (
        ("FIXATION_MAPS", "fixation_maps"),
        ("SALIENCY_MAPS", "saliency_maps"),
    ):
        legacy_maps = legacy_path / legacy_name
        target_maps = new_path / normalized_name
        if legacy_maps.exists():
            for map_file in sorted(legacy_maps.glob("*")):
                if not map_file.name.startswith("."):
                    shutil.copy2(map_file, target_maps / map_file.name)

    create_dataset_metadata(
        new_path,
        name=new_path.name,
        description=f"Migrated dataset {new_path.name}",
        authors=["Unknown"],
        year=2024,
    )
    generate_dataset_manifest(new_path)
    generate_checksums(new_path)


def generate_collection_metadata(collection_path: Path) -> list[Path]:
    """Generate metadata, manifests, and checksums for all datasets in a collection."""
    generated_paths: list[Path] = []

    for dataset_path in sorted([path for path in collection_path.iterdir() if path.is_dir()]):
        summary = inspect_dataset(dataset_path)
        mapping_rules = sorted({row["saliency_mapping_rule"] for row in summary["rows"]})
        create_dataset_metadata(
            dataset_path,
            name=dataset_path.name,
            description=f"{dataset_path.name} eye-tracking dataset bundled with FixaTons",
            authors=["Unknown"],
            year=2018,
            stimuli_count=summary["stimuli_count"],
            scanpath_dir_count=summary["scanpath_dir_count"],
            fixation_map_count=summary["fixation_map_count"],
            saliency_map_count=summary["saliency_map_count"],
            subject_count_min=summary["subject_count_min"],
            subject_count_max=summary["subject_count_max"],
            subject_count_unique=summary["subject_count_unique"],
            stimuli_extensions=summary["stimuli_extensions"],
            fixation_map_extensions=summary["fixation_map_extensions"],
            saliency_map_extensions=summary["saliency_map_extensions"],
            hidden_files=summary["hidden_files"],
            empty_scanpaths=summary["empty_scanpaths"],
            mismatches=summary["mismatches"],
            saliency_mapping_rules=mapping_rules,
        )
        generated_paths.append(generate_dataset_manifest(dataset_path))
        generate_checksums(dataset_path)
        generated_paths.append(dataset_path / "metadata.json")
        generated_paths.append(dataset_path / "checksums.md5")

    return generated_paths
