"""Deterministic regression tests for core metric functions."""

import math

import numpy as np

import FixaTons as ft


def test_auc_judd_is_high_for_perfect_prediction() -> None:
    saliency_map = np.array([[0.1, 0.2], [0.3, 1.0]], dtype=np.float32)
    fixation_map = np.array([[0, 0], [0, 1]], dtype=np.uint8)

    score = ft.auc_judd(saliency_map, fixation_map, jitter=False)

    assert math.isclose(score, 5.0 / 6.0, rel_tol=1e-6)


def test_nss_is_positive_for_fixated_salient_location() -> None:
    saliency_map = np.array([[0.0, 1.0], [0.0, 0.0]], dtype=np.float32)
    fixation_map = np.array([[0, 1], [0, 0]], dtype=np.uint8)

    score = ft.nss(saliency_map, fixation_map)

    assert score > 1.0


def test_kl_divergence_is_zero_for_identical_distributions() -> None:
    saliency_map = np.array([[0.2, 0.3], [0.1, 0.4]], dtype=np.float32)

    score = ft.kl_divergence(saliency_map, saliency_map)

    assert math.isclose(score, 0.0, abs_tol=1e-10)


def test_string_edit_distance_returns_expected_strings_and_distance() -> None:
    scanpath_1 = np.array([[10, 10], [90, 90]], dtype=np.float32)
    scanpath_2 = np.array([[10, 10], [10, 90]], dtype=np.float32)

    distance, string_1, string_2 = ft.string_edit_distance(
        scanpath_1, scanpath_2, stimulus_width=100, stimulus_height=100, grid_size=2
    )

    assert string_1 == "ad"
    assert string_2 == "ac"
    assert distance == 1


def test_time_delay_embedding_distance_is_zero_for_identical_scanpaths() -> None:
    scanpath = np.array([[0, 0], [1, 1], [2, 2]], dtype=np.float32)

    score = ft.time_delay_embedding_distance(scanpath, scanpath, k=2)

    assert score == 0.0


def test_scaled_time_delay_embedding_distance_is_one_for_identical_scanpaths() -> None:
    scanpath = np.array([[0, 0], [10, 10], [20, 20]], dtype=np.float32)
    image = np.zeros((100, 100, 3), dtype=np.uint8)

    score = ft.scaled_time_delay_embedding_distance(scanpath, scanpath, image)

    assert math.isclose(score, 1.0, rel_tol=1e-6)


def test_scanmatch_metric_is_one_for_identical_scanpaths() -> None:
    scanpath = np.array(
        [
            [10.0, 10.0, 0.0, 0.2],
            [20.0, 20.0, 0.2, 0.5],
            [30.0, 30.0, 0.5, 0.8],
        ]
    )

    score = ft.scanmatch_metric(scanpath, scanpath, stimulus_width=100, stimulus_height=100)

    assert math.isclose(score, 1.0, rel_tol=1e-6)
