# Tutorials

This folder defines the recommended learning path for FixaTons.

## Suggested Order

1. `Tutorial.ipynb`
   - Main onboarding notebook
   - Covers dataset discovery, loading, visualization, metrics, and validation
   - Uses `SIENA12` as the starter dataset

## What A Good Tutorial Session Should Teach

- How FixaTons finds datasets on disk
- The difference between a stimulus, fixation map, saliency map, and scanpath
- When to use saliency metrics versus scanpath metrics
- How to validate bundled or external datasets before analysis

## Key Files To Explore After The Main Notebook

- [README.md](/Users/dariozanca/Documents/GitHub/FixaTons/README.md)
- [Dataset/SIENA12/metadata.json](/Users/dariozanca/Documents/GitHub/FixaTons/Dataset/SIENA12/metadata.json)
- [Dataset/SIENA12/manifest.csv](/Users/dariozanca/Documents/GitHub/FixaTons/Dataset/SIENA12/manifest.csv)
- [FixaTons/dataset_utils.py](/Users/dariozanca/Documents/GitHub/FixaTons/FixaTons/dataset_utils.py)
- [tests/test_metrics.py](/Users/dariozanca/Documents/GitHub/FixaTons/tests/test_metrics.py)

## Future Notebook Ideas

- `tutorials/01_dataset_exploration.ipynb`
- `tutorials/02_saliency_metrics.ipynb`
- `tutorials/03_scanpath_metrics.ipynb`
- `tutorials/04_dataset_validation.ipynb`
- `tutorials/05_mini_research_workflow.ipynb`
