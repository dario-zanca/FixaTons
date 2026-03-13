# Contributing A Dataset

This guide describes how to add a new eye-tracking dataset to the FixaTons repository in a way that is consistent, reviewable, and easy to validate.

## Before You Start

Only contribute a dataset if all of the following are true:

- You have redistribution rights or explicit permission to include the dataset in this repository.
- The dataset has a clear citation or source publication.
- The dataset contains temporal scanpath information, not only static fixation maps.
- Stimuli, scanpaths, fixation maps, and saliency maps can be paired reliably.

If redistribution is not allowed, do not commit the raw dataset. In that case, prefer contributing metadata, validation rules, and a documented download/conversion workflow instead.

## Required Repository Layout

Datasets in this repository currently live under `Dataset/`.

The canonical layout for a dataset named `MYDATASET` is:

```text
Dataset/
└── MYDATASET/
    ├── STIMULI/
    ├── SCANPATHS/
    │   └── STIMULUS_STEM/
    │       └── SUBJECT_ID
    ├── FIXATION_MAPS/
    ├── SALIENCY_MAPS/
    ├── metadata.json
    ├── manifest.csv
    └── checksums.md5
```

Notes:

- `STIMULI/` contains the original images.
- `SCANPATHS/<stimulus_stem>/` contains one text file per subject.
- `FIXATION_MAPS/` contains binary fixation maps aligned with the stimuli.
- `SALIENCY_MAPS/` contains saliency maps aligned with the stimuli.
- The stem of the stimulus filename should normally match:
  - the scanpath directory name
  - the fixation map filename stem
  - the saliency map filename stem

If the dataset needs a special mapping rule, document it clearly and add code support plus tests.

## Required Data Conventions

### Stimuli

- Store the original images in `STIMULI/`.
- Use a consistent image extension within a dataset when possible.

### Scanpaths

Each scanpath file must contain one fixation per row in the format:

```text
x_pixel y_pixel start_time end_time
```

Conventions:

- coordinates are in image pixels
- time values are in seconds
- one file per subject per stimulus
- empty files should be avoided

### Fixation Maps

- Binary maps representing fixated locations
- Must be aligned with the corresponding stimulus

### Saliency Maps

- Human-derived saliency maps aligned with the corresponding stimulus
- Must be pairable to each stimulus either directly or through an explicit, documented mapping rule

## Required Artifact Generation

After adding the raw dataset files, generate the machine-readable artifacts:

```bash
python -m FixaTons manifest Dataset/MYDATASET
python -m FixaTons validate Dataset/MYDATASET
python -m FixaTons verify-checksums Dataset/MYDATASET
```

Or regenerate artifacts for the entire collection:

```bash
python -m FixaTons generate --collection Dataset
```

This creates or refreshes:

- `manifest.csv`
- `checksums.md5`
- `metadata.json` if you use the collection-wide generation path

## What `metadata.json` Should Capture

At minimum:

- dataset name
- description
- citation year
- file extensions used
- number of stimuli
- subject count range
- known empty scanpaths
- known hidden files
- mismatch summary
- any dataset-specific saliency mapping rules

The repository already contains examples:

- [Dataset/SIENA12/metadata.json](/Users/dariozanca/Documents/GitHub/FixaTons/Dataset/SIENA12/metadata.json)
- [Dataset/TORONTO/metadata.json](/Users/dariozanca/Documents/GitHub/FixaTons/Dataset/TORONTO/metadata.json)

## What `manifest.csv` Should Capture

The manifest is the most important review artifact. It should make per-stimulus completeness obvious.

Expected columns:

- `stimulus_id`
- `stimulus_file`
- `fixation_map_file`
- `saliency_map_file`
- `scanpath_dir`
- `subject_count`
- `empty_scanpath_files`
- `is_complete`
- `saliency_mapping_rule`

Example:

- [Dataset/TORONTO/manifest.csv](/Users/dariozanca/Documents/GitHub/FixaTons/Dataset/TORONTO/manifest.csv)

## Validation Checklist

Before opening a pull request, confirm all of the following:

- The dataset is located under `Dataset/MYDATASET/`
- All expected subfolders exist
- Stimulus basenames match scanpath directories
- Fixation maps pair correctly with stimuli
- Saliency maps pair correctly with stimuli
- `manifest.csv`, `metadata.json`, and `checksums.md5` exist
- `python -m FixaTons validate Dataset/MYDATASET` exits successfully
- `python -m FixaTons verify-checksums Dataset/MYDATASET` prints `ok`
- If you added a special mapping rule, you also added tests

## Worked Example

Suppose you want to add `MYDATASET`.

1. Create the dataset folders:

```bash
mkdir -p Dataset/MYDATASET/STIMULI
mkdir -p Dataset/MYDATASET/SCANPATHS
mkdir -p Dataset/MYDATASET/FIXATION_MAPS
mkdir -p Dataset/MYDATASET/SALIENCY_MAPS
```

2. Copy the raw files into those folders.

3. Ensure one stimulus called `image_001.jpg` has:

- `Dataset/MYDATASET/STIMULI/image_001.jpg`
- `Dataset/MYDATASET/SCANPATHS/image_001/<subject files>`
- `Dataset/MYDATASET/FIXATION_MAPS/image_001.png`
- `Dataset/MYDATASET/SALIENCY_MAPS/image_001.png`

4. Generate artifacts:

```bash
python -m FixaTons manifest Dataset/MYDATASET
python -m FixaTons validate Dataset/MYDATASET
python -m FixaTons verify-checksums Dataset/MYDATASET
```

5. Inspect the generated files:

- `Dataset/MYDATASET/manifest.csv`
- `Dataset/MYDATASET/checksums.md5`

6. If needed, regenerate metadata for the full collection:

```bash
python -m FixaTons generate --collection Dataset
```

## Common Problems

### Hidden files such as `.DS_Store`

These pollute counts and validation summaries. Remove them before committing.

### Empty scanpath files

These should usually be removed or documented. If you keep them, the validator will report them.

### Mismatched filename stems

Example:

- stimulus: `1.jpg`
- saliency map: `d1.jpg`

If this is unavoidable, document the mapping rule and add explicit support plus tests.

### Mixed conventions across stimuli

If some scanpath folders match stimulus stems and others do not, the dataset should be normalized before contribution.

## Pull Request Expectations

A good dataset PR should include:

- the dataset files or the allowed subset being contributed
- generated `metadata.json`
- generated `manifest.csv`
- generated `checksums.md5`
- a citation/source note in the PR description
- a short note if the dataset needs special loader behavior

If the dataset required loader changes, mention the exact rule and point to the corresponding tests.
