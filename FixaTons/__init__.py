"""Public package API for FixaTons."""

from __future__ import annotations

import os
import warnings
from pathlib import Path

__version__ = "1.0.0"
__author__ = "Dario Zanca"
__email__ = "dariozanca@gmail.com"


def _resolve_default_datasets_path() -> Path:
    root = Path(__file__).resolve().parent.parent
    candidates = [root / "Dataset", root / "Datasets"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


class _DeprecatedGetProxy:
    """Backward-compatible grouped getters."""

    def __init__(self, *, stimulus, fixation_map, saliency_map, scanpath) -> None:
        self._mapping = {
            "stimulus": stimulus,
            "fixation_map": fixation_map,
            "saliency_map": saliency_map,
            "scanpath": scanpath,
        }

    def __getattr__(self, name: str):
        if name not in self._mapping:
            raise AttributeError(name)
        warnings.warn(
            "'ft.get' is deprecated; use direct top-level loaders like 'ft.stimulus(...)' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._mapping[name]


COLLECTION_PATH = Path(
    os.environ.get("FIXATONS_DATASETS_PATH", _resolve_default_datasets_path())
)

from . import dataset_utils, metrics, stats
from .data import fixation_map, info, saliency_map, scanpath, stimulus
from .metrics import (
    auc_judd,
    auc_shuffled,
    compute_rqa_metrics,
    euclidean_distance,
    information_gain,
    kl_divergence,
    multimatch_metric,
    nss,
    scaled_time_delay_embedding_distance,
    scanmatch_metric,
    scanpath_to_string,
    string_based_time_delay_embedding_distance,
    string_edit_distance,
    time_delay_embedding_distance,
)
from .stats import fps, sac_len, statistics
from .visualization import show

get = _DeprecatedGetProxy(
    stimulus=stimulus,
    fixation_map=fixation_map,
    saliency_map=saliency_map,
    scanpath=scanpath,
)

__all__ = [
    "COLLECTION_PATH",
    "__version__",
    "info",
    "get",
    "show",
    "metrics",
    "stats",
    "dataset_utils",
    "stimulus",
    "fixation_map",
    "saliency_map",
    "scanpath",
    "statistics",
    "fps",
    "sac_len",
    "auc_judd",
    "auc_shuffled",
    "kl_divergence",
    "nss",
    "information_gain",
    "euclidean_distance",
    "string_edit_distance",
    "scanpath_to_string",
    "time_delay_embedding_distance",
    "scaled_time_delay_embedding_distance",
    "string_based_time_delay_embedding_distance",
    "compute_rqa_metrics",
    "scanmatch_metric",
    "multimatch_metric",
]
