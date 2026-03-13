"""Basic integration tests for the public FixaTons API."""

import csv
import json
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np

import FixaTons as ft
from FixaTons import dataset_utils


DATASET_NAME = "SIENA12"
STIMULUS_NAME = "sunset.jpg"
DATASETS = ["KOOTSTRA", "MIT1003", "SIENA12", "TORONTO"]


def test_collection_path_exists() -> None:
    assert isinstance(ft.COLLECTION_PATH, Path)
    assert ft.COLLECTION_PATH.exists()


def test_dataset_discovery_uses_included_samples() -> None:
    datasets = ft.info.datasets()
    assert DATASET_NAME in datasets


def test_stimuli_and_subjects_are_discoverable() -> None:
    stimuli = ft.info.stimuli(DATASET_NAME)
    subjects = ft.info.subjects(DATASET_NAME, STIMULUS_NAME)

    assert STIMULUS_NAME in stimuli
    assert len(subjects) > 0


def test_direct_loaders_return_real_data() -> None:
    stimulus = ft.stimulus(DATASET_NAME, STIMULUS_NAME)
    fixation_map = ft.fixation_map(DATASET_NAME, STIMULUS_NAME)
    saliency_map = ft.saliency_map(DATASET_NAME, STIMULUS_NAME)
    scanpath = ft.scanpath(DATASET_NAME, STIMULUS_NAME)

    assert stimulus is not None and stimulus.ndim == 3
    assert fixation_map is not None and fixation_map.ndim == 2
    assert saliency_map is not None and saliency_map.ndim == 2
    assert scanpath is not None and scanpath.shape[1] == 4


def test_legacy_grouped_api_matches_direct_api() -> None:
    direct = ft.stimulus(DATASET_NAME, STIMULUS_NAME)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        grouped = ft.get.stimulus(DATASET_NAME, STIMULUS_NAME)

    assert direct is not None
    assert grouped is not None
    assert any("deprecated" in str(w.message).lower() for w in caught)
    np.testing.assert_array_equal(direct, grouped)


def test_invalid_inputs_fail_gracefully() -> None:
    assert ft.stimulus("missing", "fake.jpg") is None
    assert ft.fixation_map("missing", "fake.jpg") is None
    assert ft.saliency_map("missing", "fake.jpg") is None
    assert ft.scanpath("missing", "fake.jpg") is None
    assert ft.info.stimuli("missing") == []


def test_metrics_api_is_exposed() -> None:
    assert callable(ft.auc_judd)
    assert callable(ft.metrics.auc_judd)
    assert callable(ft.metrics.scanmatch_metric)


def test_auc_judd_accepts_loaded_maps() -> None:
    fixation_map = ft.fixation_map(DATASET_NAME, STIMULUS_NAME)
    saliency_map = ft.saliency_map(DATASET_NAME, STIMULUS_NAME)

    assert fixation_map is not None
    assert saliency_map is not None

    score = ft.auc_judd(saliency_map, fixation_map, jitter=False)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_statistics_api_returns_numeric_summary() -> None:
    fixations_per_second, saccade_length = ft.statistics(DATASET_NAME)

    assert isinstance(fixations_per_second, float)
    assert isinstance(saccade_length, float)
    assert fixations_per_second > 0
    assert saccade_length > 0


def test_toronto_saliency_map_uses_dataset_specific_mapping() -> None:
    saliency_map = ft.saliency_map("TORONTO", "1.jpg")
    fixation_map = ft.fixation_map("TORONTO", "1.jpg")

    assert saliency_map is not None
    assert fixation_map is not None
    assert saliency_map.shape == fixation_map.shape


def test_dataset_inspection_and_validation_surface_known_issues() -> None:
    summary = dataset_utils.inspect_dataset(ft.COLLECTION_PATH / "SIENA12")
    validation = dataset_utils.validate_dataset_structure(ft.COLLECTION_PATH / "SIENA12")

    assert summary["stimuli_count"] == 12
    assert len(summary["empty_scanpaths"]) == 2
    assert validation["has_empty_scanpaths"] is True
    assert validation["complete_pairings"] is True


def test_generated_dataset_artifacts_exist_and_verify() -> None:
    for dataset_name in DATASETS:
        dataset_path = ft.COLLECTION_PATH / dataset_name
        metadata_path = dataset_path / "metadata.json"
        manifest_path = dataset_path / "manifest.csv"
        checksums_path = dataset_path / "checksums.md5"

        assert metadata_path.exists()
        assert manifest_path.exists()
        assert checksums_path.exists()

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        with open(manifest_path, "r", encoding="utf-8", newline="") as file_handle:
            rows = list(csv.DictReader(file_handle))

        assert metadata["name"] == dataset_name
        assert metadata["stimuli_count"] == len(rows)
        assert dataset_utils.verify_checksums(dataset_path) == []


def test_cli_validate_and_verify_checksums() -> None:
    dataset_path = ft.COLLECTION_PATH / "TORONTO"

    validate_run = subprocess.run(
        [sys.executable, "-m", "FixaTons", "validate", str(dataset_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert validate_run.returncode == 0
    assert '"complete_pairings": true' in validate_run.stdout.lower()

    verify_run = subprocess.run(
        [sys.executable, "-m", "FixaTons", "verify-checksums", str(dataset_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert verify_run.returncode == 0
    assert verify_run.stdout.strip() == "ok"


def test_legacy_metric_aliases_warn() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        metric_fn = ft.metrics.AUC_Judd

    assert callable(metric_fn)
    assert any("deprecated" in str(w.message).lower() for w in caught)
