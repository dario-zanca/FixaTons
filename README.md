# FixaTons

[![PyPI version](https://badge.fury.io/py/FixaTons.svg)](https://pypi.org/project/FixaTons/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FixaTons is a Python toolkit for working with eye-tracking datasets, fixation maps, saliency maps, and scanpath similarity metrics.

## What It Provides

- Dataset discovery helpers for bundled or externally mounted datasets
- Direct loading of stimuli, saliency maps, fixation maps, and subject scanpaths
- Visualization utilities for maps and scanpaths
- Saliency metrics such as AUC-Judd, shuffled AUC, KL divergence, NSS, and information gain
- Scanpath metrics such as string edit distance, time-delay embedding, RQA, ScanMatch, and MultiMatch
- Basic statistical summaries over datasets

## Installation

```bash
pip install FixaTons
```

For local development:

```bash
git clone https://github.com/dariozanca/FixaTons.git
cd FixaTons
pip install -e .[dev]
```

## Dataset Location

By default, the package looks for datasets in:

- `Dataset/`
- `Datasets/`

You can override that with:

```bash
export FIXATONS_DATASETS_PATH=/path/to/datasets
```

The current repository already includes sample datasets under `Dataset/`.

## Tutorial

Start with the main notebook:

- [Tutorial.ipynb](/Users/dariozanca/Documents/GitHub/FixaTons/Tutorial.ipynb)

The tutorial path and follow-up material are indexed in:

- [docs/tutorials/README.md](/Users/dariozanca/Documents/GitHub/FixaTons/docs/tutorials/README.md)

## Contributing Datasets

If you want to add another dataset to the repository, use the dataset contribution guide:

- [docs/contributing-datasets.md](/Users/dariozanca/Documents/GitHub/FixaTons/docs/contributing-datasets.md)

## Quick Start

```python
import FixaTons as ft

dataset = "SIENA12"
stimulus_name = "sunset.jpg"

print(ft.info.datasets())
print(ft.info.subjects(dataset, stimulus_name)[:3])

stimulus = ft.stimulus(dataset, stimulus_name)
fixation_map = ft.fixation_map(dataset, stimulus_name)
saliency_map = ft.saliency_map(dataset, stimulus_name)
scanpath = ft.scanpath(dataset, stimulus_name)

score = ft.auc_judd(saliency_map, fixation_map, jitter=False)
print(score)
```

Legacy grouped access is still available:

```python
stimulus = ft.get.stimulus(dataset, stimulus_name)
scanpath = ft.get.scanpath(dataset, stimulus_name)
```

## Included Dataset Layout

The package supports both the original legacy layout and a normalized lowercase layout.

Legacy layout:

```text
Dataset/
└── DATASET_NAME/
    ├── STIMULI/
    ├── SCANPATHS/
    │   └── IMAGE_ID/
    │       └── SUBJECT_ID
    ├── FIXATION_MAPS/
    └── SALIENCY_MAPS/
```

Normalized layout:

```text
dataset_name/
├── stimuli/
├── scanpaths/
├── fixation_maps/
├── saliency_maps/
├── metadata.json
└── checksums.md5
```

Utility helpers are exposed for validation, checksum generation, and migration:

```python
ft.validate_dataset_structure(path)
ft.generate_checksums(path)
ft.verify_checksums(path)
ft.migrate_legacy_structure(old_path, new_path)
```

Command line usage is also available:

```bash
fixatons-datasets inspect Dataset/SIENA12
fixatons-datasets validate Dataset/TORONTO
fixatons-datasets generate --collection Dataset
```

## Main API

Information helpers:

- `ft.info.datasets()`
- `ft.info.stimuli(dataset_name)`
- `ft.info.subjects(dataset_name, stimulus_name)`

Direct data access:

- `ft.stimulus(dataset_name, stimulus_name)`
- `ft.fixation_map(dataset_name, stimulus_name)`
- `ft.saliency_map(dataset_name, stimulus_name)`
- `ft.scanpath(dataset_name, stimulus_name, subject="...")`

Statistics:

- `ft.statistics(dataset_name=None)`
- `ft.fps(scanpath)`
- `ft.sac_len(scanpath)`

Metrics:

- `ft.auc_judd(...)`
- `ft.auc_shuffled(...)`
- `ft.kl_divergence(...)`
- `ft.nss(...)`
- `ft.information_gain(...)`
- `ft.string_edit_distance(...)`
- `ft.scaled_time_delay_embedding_distance(...)`
- `ft.compute_rqa_metrics(...)`
- `ft.scanmatch_metric(...)`
- `ft.multimatch_metric(...)`

## Citation

If you use FixaTons in research, cite:

```bibtex
@article{zanca2018fixatons,
  title={FixaTons: A collection of human fixations datasets and metrics for scanpath similarity},
  author={Zanca, Dario},
  journal={arXiv preprint arXiv:1802.02534},
  year={2018}
}
```

Technical report: https://arxiv.org/abs/1802.02534

## License

MIT. See `LICENSE`.
