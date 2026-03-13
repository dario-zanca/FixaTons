"""Backward-compatible module shim for the packaged FixaTons API."""

from __future__ import annotations

import warnings

import FixaTons as ft

warnings.warn(
    "Importing from 'FixaTons.py' is deprecated; use 'import FixaTons as ft' instead.",
    DeprecationWarning,
    stacklevel=2,
)

info = ft.info
get = ft.get
show = ft.show
metrics = ft.metrics
stats = ft.stats
stimulus = ft.stimulus
fixation_map = ft.fixation_map
saliency_map = ft.saliency_map
scanpath = ft.scanpath
statistics = ft.statistics
fps = ft.fps
sac_len = ft.sac_len
COLLECTION_PATH = ft.COLLECTION_PATH
__version__ = ft.__version__

__all__ = [
    "info",
    "get",
    "show",
    "metrics",
    "stats",
    "stimulus",
    "fixation_map",
    "saliency_map",
    "scanpath",
    "statistics",
    "fps",
    "sac_len",
    "COLLECTION_PATH",
    "__version__",
]
