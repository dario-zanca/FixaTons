"""
Saliency map evaluation metrics.

This module contains functions for evaluating how well saliency maps predict
human fixation locations, including AUC, KL-divergence, NSS, and information gain.
"""

#########################################################################################

# IMPORT EXTERNAL LIBRARIES

import numpy as np
from copy import copy

#########################################################################################

def auc_judd(saliency_map: np.ndarray, fixation_map: np.ndarray,
             jitter: bool = True, to_plot: bool = False) -> float:
    """
    Compute Area Under the ROC Curve (AUC) - Judd version.

    This measures how well the saliency map predicts ground truth human fixations.
    ROC curve is created by sweeping through threshold values determined by the
    range of saliency map values at fixation locations.

    Parameters
    ----------
    saliency_map : np.ndarray
        The saliency map to evaluate
    fixation_map : np.ndarray
        Binary human fixation map (ground truth)
    jitter : bool, default=True
        Add tiny random noise to avoid uniform regions
    to_plot : bool, default=False
        Whether to display the ROC curve

    Returns
    -------
    float
        AUC score (area under ROC curve)

    References
    ----------
    Judd, T., Ehinger, K., Durand, F., & Torralba, A. (2009).
    Learning to predict where humans look. In ICCV.
    """
    # If there are no fixations to predict, return NaN
    if not fixation_map.any():
        print('Error: no fixation_map')
        return float('nan')

    # Resize saliency map if needed
    if saliency_map.shape != fixation_map.shape:
        from PIL import Image
        saliency_map = np.array(Image.fromarray(saliency_map).resize(
            (fixation_map.shape[1], fixation_map.shape[0])))

    # Jitter saliency maps to disrupt ties
    if jitter:
        saliency_map = saliency_map + np.random.random(saliency_map.shape) / 10**7

    # Normalize saliency map to [0,1]
    saliency_map = (saliency_map - saliency_map.min()) / \
                   (saliency_map.max() - saliency_map.min())

    if np.isnan(saliency_map).all():
        print('NaN saliency_map')
        return float('nan')

    S = saliency_map.flatten()
    F = fixation_map.flatten()

    Sth = S[F > 0]  # saliency values at fixation locations
    Nfixations = len(Sth)
    Npixels = len(S)

    allthreshes = sorted(Sth, reverse=True)
    tp = np.zeros((Nfixations + 2))
    fp = np.zeros((Nfixations + 2))
    tp[0], tp[-1] = 0, 1
    fp[0], fp[-1] = 0, 1

    for i in range(Nfixations):
        thresh = allthreshes[i]
        aboveth = (S >= thresh).sum()
        tp[i + 1] = float(i + 1) / Nfixations
        fp[i + 1] = float(aboveth - i) / (Npixels - Nfixations)

    score = np.trapezoid(tp, x=fp)

    if to_plot:
        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(1, 2, 1)
        ax.matshow(saliency_map, cmap='gray')
        ax.set_title('Saliency Map with Fixations')
        [y, x] = np.nonzero(fixation_map)
        s = saliency_map.shape
        plt.axis((-.5, s[1] - .5, s[0] - .5, -.5))
        plt.plot(x, y, 'ro')

        ax = fig.add_subplot(1, 2, 2)
        plt.plot(fp, tp, '.b-')
        ax.set_title(f'AUC: {score:.3f}')
        plt.axis((0, 1, 0, 1))
        plt.show()

    return score


def auc_shuffled(saliency_map: np.ndarray, fixation_map: np.ndarray,
                 other_map: np.ndarray, n_splits: int,
                 step_size: float = 0.1, to_plot: bool = False) -> float:
    """
    Compute shuffled AUC for saliency map evaluation.

    Parameters
    ----------
    saliency_map : np.ndarray
        The saliency map to evaluate
    fixation_map : np.ndarray
        Binary human fixation map
    other_map : np.ndarray
        Binary fixation map from other images (baseline)
    n_splits : int
        Number of random splits for shuffling
    step_size : float, default=0.1
        Step size for threshold sweeping
    to_plot : bool, default=False
        Whether to display ROC curve

    Returns
    -------
    float
        Mean AUC across random splits
    """
    if not fixation_map.any():
        print('Error: no fixation_map')
        return float('nan')

    if saliency_map.shape != fixation_map.shape:
        from PIL import Image
        saliency_map = np.array(Image.fromarray(saliency_map).resize(
            (fixation_map.shape[1], fixation_map.shape[0])))

    if np.isnan(saliency_map).all():
        print('NaN saliency_map')
        return float('nan')

    # Normalize saliency map
    saliency_map = (saliency_map - saliency_map.min()) / \
                   (saliency_map.max() - saliency_map.min())

    S = saliency_map.flatten(order='F')
    F = fixation_map.flatten(order='F')
    Oth = other_map.flatten(order='F')

    Sth = S[F > 0]  # saliency at fixations
    Nfixations = len(Sth)

    # Sample random fixation locations from other images
    ind = np.nonzero(Oth)[0]
    Nfixations_oth = min(Nfixations, len(ind))
    randfix = np.empty((Nfixations_oth, n_splits))
    randfix[:] = np.nan

    for i in range(n_splits):
        randind = np.random.permutation(ind)[:Nfixations_oth]
        randfix[:, i] = S[randind]

    # Calculate AUC for each random split
    auc_scores = np.empty(n_splits)
    auc_scores[:] = np.nan

    for s in range(n_splits):
        curfix = randfix[:, s]
        thresholds = np.arange(0, max(np.maximum(Sth, curfix)), step_size)

        tp = np.zeros(len(thresholds) + 2)
        fp = np.zeros(len(thresholds) + 2)
        tp[0], tp[-1] = 0, 1
        fp[0], fp[-1] = 0, 1

        for i, thresh in enumerate(thresholds):
            tp[i+1] = (Sth >= thresh).sum() / Nfixations
            fp[i+1] = (curfix >= thresh).sum() / Nfixations_oth

        auc_scores[s] = np.trapezoid(tp, x=fp)

    score = np.mean(auc_scores)

    if to_plot:
        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.add_subplot(1, 2, 1)
        ax.matshow(saliency_map, cmap='gray')
        ax.set_title('Saliency Map with Fixations')
        [y, x] = np.nonzero(fixation_map)
        s = saliency_map.shape
        plt.axis((-.5, s[1] - .5, s[0] - .5, -.5))
        plt.plot(x, y, 'ro')

        ax = fig.add_subplot(1, 2, 2)
        plt.plot(fp, tp, '.b-')
        ax.set_title(f'Shuffled AUC: {score:.3f}')
        plt.axis((0, 1, 0, 1))
        plt.show()

    return score


def kl_divergence(saliency_map: np.ndarray, fixation_map: np.ndarray) -> float:
    """
    Compute Kullback-Leibler divergence between saliency maps.

    Non-symmetric measure of information lost when using saliency_map
    to estimate fixation_map.

    Parameters
    ----------
    saliency_map : np.ndarray
        Predicted saliency map
    fixation_map : np.ndarray
        Ground truth fixation map

    Returns
    -------
    float
        KL-divergence score
    """
    map1 = saliency_map.astype(float)
    map2 = fixation_map.astype(float)

    # Resize if needed
    if map1.shape != map2.shape:
        from PIL import Image
        map1 = np.array(Image.fromarray(map1).resize(
            (map2.shape[1], map2.shape[0])))

    # Normalize to probability distributions
    if map1.any():
        map1 = map1 / map1.sum()
    if map2.any():
        map2 = map2 / map2.sum()

    # Compute KL-divergence
    eps = 10**-12
    score = map2 * np.log(eps + map2 / (map1 + eps))

    return score.sum()


def nss(saliency_map: np.ndarray, fixation_map: np.ndarray) -> float:
    """
    Compute Normalized Scanpath Saliency (NSS).

    Average of normalized saliency values at human fixation locations.

    Parameters
    ----------
    saliency_map : np.ndarray
        The saliency map
    fixation_map : np.ndarray
        Binary human fixation map

    Returns
    -------
    float
        NSS score
    """
    if not fixation_map.any():
        print('Error: no fixation_map')
        return float('nan')

    # Resize if needed
    map1 = saliency_map
    if saliency_map.shape != fixation_map.shape:
        from PIL import Image
        map1 = np.array(Image.fromarray(saliency_map).resize(
            (fixation_map.shape[1], fixation_map.shape[0])))

    # Normalize to [0,1]
    if map1.max() != 0:
        map1 = map1.astype(float) / map1.max()

    # Standardize (zero mean, unit std)
    if map1.std(ddof=1) != 0:
        map1 = (map1 - map1.mean()) / map1.std(ddof=1)

    # Mean value at fixation locations
    score = map1[fixation_map.astype(bool)].mean()

    return score


def information_gain(saliency_map: np.ndarray, fixation_map: np.ndarray,
                    baseline_map: np.ndarray) -> float:
    """
    Compute information gain of saliency_map over baseline_map.

    Based on Kummerer et al. (2015).

    Parameters
    ----------
    saliency_map : np.ndarray
        The saliency map to evaluate
    fixation_map : np.ndarray
        Binary human fixation map
    baseline_map : np.ndarray
        Baseline saliency map (e.g., from other images)

    Returns
    -------
    float
        Information gain score
    """
    map1 = np.resize(saliency_map, fixation_map.shape)
    mapb = np.resize(baseline_map, fixation_map.shape)

    # Normalize and vectorize
    map1 = (map1.flatten(order='F') - np.min(map1)) / \
           (np.max(map1) - np.min(map1))
    mapb = (mapb.flatten(order='F') - np.min(mapb)) / \
           (np.max(mapb) - np.min(mapb))

    # Turn into distributions
    map1 /= np.sum(map1)
    mapb /= np.sum(mapb)

    fixation_map = fixation_map.flatten(order='F')
    locs = fixation_map > 0

    eps = 2.2204e-16
    score = np.mean(np.log2(eps + map1[locs]) - np.log2(eps + mapb[locs]))

    return score
