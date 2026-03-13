"""Data loading helpers."""

from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from .. import COLLECTION_PATH


def _find_file_path(
    dataset_name: str, subfolder: str, filename: str, legacy_folder: Optional[str] = None
) -> Optional[Path]:
    dataset_path = COLLECTION_PATH / dataset_name

    new_path = dataset_path / subfolder / filename
    if new_path.exists():
        return new_path

    if legacy_folder:
        legacy_path = dataset_path / legacy_folder / filename
        if legacy_path.exists():
            return legacy_path

    return None


def _find_map_path(
    dataset_name: str, stimulus_name: str, subfolder: str, legacy_folder: str
) -> Optional[Path]:
    file_name, _ = os.path.splitext(stimulus_name)
    dataset_path = COLLECTION_PATH / dataset_name

    for folder_name in (subfolder, legacy_folder):
        folder = dataset_path / folder_name
        if not folder.exists():
            continue
        special_candidates = [file_name]
        if dataset_name.upper() == "TORONTO" and subfolder == "saliency_maps":
            special_candidates.append(f"d{file_name}")
        for candidate in sorted(folder.iterdir()):
            if candidate.is_file() and candidate.stem in special_candidates:
                return candidate
    return None


def stimulus(dataset_name: str, stimulus_name: str) -> Optional[np.ndarray]:
    """Return the stimulus image matrix."""
    path = _find_file_path(dataset_name, "stimuli", stimulus_name, "STIMULI")
    if path is None:
        return None
    return cv2.imread(str(path), cv2.IMREAD_COLOR)


def fixation_map(dataset_name: str, stimulus_name: str) -> Optional[np.ndarray]:
    """Return a binary fixation map."""
    path = _find_map_path(
        dataset_name, stimulus_name, subfolder="fixation_maps", legacy_folder="FIXATION_MAPS"
    )
    if path is None:
        return None

    fixation_map_data = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if fixation_map_data is None:
        return None

    binary_map = fixation_map_data.astype(np.uint8)
    binary_map[binary_map > 0] = 1
    return binary_map


def saliency_map(dataset_name: str, stimulus_name: str) -> Optional[np.ndarray]:
    """Return the saliency map."""
    path = _find_map_path(
        dataset_name, stimulus_name, subfolder="saliency_maps", legacy_folder="SALIENCY_MAPS"
    )
    if path is None:
        return None

    saliency_map_data = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if saliency_map_data is None:
        return None

    if saliency_map_data.max() > 1:
        return saliency_map_data.astype(np.float32) / 255.0
    return saliency_map_data.astype(np.float32)


def scanpath(
    dataset_name: str, stimulus_name: str, subject: str = ""
) -> Optional[np.ndarray]:
    """Return the scanpath matrix with columns ``x, y, start_t, end_t``."""
    file_name, _ = os.path.splitext(stimulus_name)
    dataset_path = COLLECTION_PATH / dataset_name

    legacy_dir = dataset_path / "SCANPATHS" / file_name
    lowered_dir = dataset_path / "scanpaths"

    if legacy_dir.exists():
        if not subject:
            subjects_list = sorted([f.name for f in legacy_dir.iterdir() if f.is_file()])
            if not subjects_list:
                return None
            subject = random.choice(subjects_list)
        scanpath_file_path = legacy_dir / subject
    elif lowered_dir.exists():
        if not subject:
            prefix = f"{file_name}_subject_"
            candidates = sorted(
                [f for f in lowered_dir.iterdir() if f.is_file() and f.name.startswith(prefix)]
            )
            if not candidates:
                return None
            scanpath_file_path = random.choice(candidates)
        else:
            scanpath_file_path = lowered_dir / f"{file_name}_subject_{subject}"
    else:
        return None

    if not scanpath_file_path.exists():
        return None

    try:
        if scanpath_file_path.stat().st_size == 0:
            return np.empty((0, 4), dtype=np.float64)
        scanpath_data = np.loadtxt(scanpath_file_path, dtype=np.float64)
    except (OSError, ValueError):
        return None

    if scanpath_data.size == 0:
        return np.empty((0, 4), dtype=np.float64)
    return np.atleast_2d(scanpath_data)
