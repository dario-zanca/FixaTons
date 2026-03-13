"""Visual attention and scanpath similarity metrics."""

from __future__ import annotations

import warnings

from .rqa import RQA
from .saliency import auc_judd, auc_shuffled, information_gain, kl_divergence, nss
from .scanpath import (
    compute_rqa_metrics,
    euclidean_distance,
    multimatch_metric,
    scaled_time_delay_embedding_distance,
    scanmatch_metric,
    scanpath_to_string,
    string_based_time_delay_embedding_distance,
    string_edit_distance,
    time_delay_embedding_distance,
)

_LEGACY_ALIASES = {
    "AUC_Judd": auc_judd,
    "AUC_shuffled": auc_shuffled,
    "KLdiv": kl_divergence,
    "NSS": nss,
    "InfoGain": information_gain,
    "scanMatch_metric": scanmatch_metric,
    "multiMatch_metric": multimatch_metric,
}


def __getattr__(name: str):
    if name not in _LEGACY_ALIASES:
        raise AttributeError(name)
    warnings.warn(
        f"'FixaTons.metrics.{name}' is deprecated; use the snake_case metric name instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _LEGACY_ALIASES[name]


__all__ = [
    "RQA",
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
