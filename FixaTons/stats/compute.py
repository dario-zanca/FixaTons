"""Statistical summaries for scanpath collections."""

from __future__ import annotations

import numpy as np

import FixaTons


def statistics(dataset_name: str | None = None) -> tuple[float, float]:
    """Compute mean fixations-per-second and mean saccade length."""
    number_of_scanpaths = 0
    fixations_per_second = 0.0
    saccade_length = 0.0

    datasets_list = (dataset_name,) if dataset_name else FixaTons.info.datasets()

    for current_dataset in datasets_list:
        for stimulus_name in FixaTons.info.stimuli(current_dataset):
            for subject_name in FixaTons.info.subjects(current_dataset, stimulus_name):
                scanpath = FixaTons.scanpath(current_dataset, stimulus_name, subject_name)
                if scanpath is None or len(scanpath) == 0:
                    continue

                number_of_scanpaths += 1
                fixations_per_second += fps(scanpath)
                saccade_length += sac_len(scanpath)

    if number_of_scanpaths == 0:
        return 0.0, 0.0

    return (
        fixations_per_second / number_of_scanpaths,
        saccade_length / number_of_scanpaths,
    )


def fps(scanpath: np.ndarray) -> float:
    if len(scanpath) == 0 or scanpath[-1, 3] == 0:
        return 0.0
    return float(len(scanpath)) / float(scanpath[-1, 3])


def sac_len(scanpath: np.ndarray) -> float:
    if len(scanpath) == 0:
        return 0.0

    saccade_sum = 0.0
    for i in np.arange(1, len(scanpath), 1):
        saccade_sum += np.sqrt(
            (scanpath[i, 0] - scanpath[i - 1, 0]) ** 2
            + (scanpath[i, 1] - scanpath[i - 1, 1]) ** 2
        )

    return saccade_sum / len(scanpath)
