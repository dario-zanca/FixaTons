"""Dataset discovery helpers."""

from __future__ import annotations

import os

from .. import COLLECTION_PATH


def _existing_dir(*candidates: str):
    for candidate in candidates:
        path = COLLECTION_PATH / candidate
        if path.exists():
            return path
    return None


def datasets() -> list[str]:
    """List available dataset names."""
    if not COLLECTION_PATH.exists():
        return []
    return sorted([d.name for d in COLLECTION_PATH.iterdir() if d.is_dir()])


def stimuli(dataset_name: str) -> list[str]:
    """List stimuli for a dataset, supporting legacy and lowercase layouts."""
    dataset_path = COLLECTION_PATH / dataset_name
    for folder_name in ("stimuli", "STIMULI"):
        stimuli_path = dataset_path / folder_name
        if stimuli_path.exists():
            return sorted([f.name for f in stimuli_path.iterdir() if f.is_file()])
    return []


def subjects(dataset_name: str, stimulus_name: str) -> list[str]:
    """List subjects for a stimulus in a dataset."""
    file_name, _ = os.path.splitext(stimulus_name)
    dataset_path = COLLECTION_PATH / dataset_name

    legacy_path = dataset_path / "SCANPATHS" / file_name
    if legacy_path.exists():
        return sorted([f.name for f in legacy_path.iterdir() if f.is_file()])

    lowered_path = dataset_path / "scanpaths"
    if lowered_path.exists():
        prefix = f"{file_name}_subject_"
        return sorted(
            [
                f.name[len(prefix) :]
                for f in lowered_path.iterdir()
                if f.is_file() and f.name.startswith(prefix)
            ]
        )

    return []
