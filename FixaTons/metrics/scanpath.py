"""
Scanpath similarity metrics.

This module contains various metrics for comparing eye movement scanpaths,
including distance-based, string-based, and advanced similarity measures.
"""

#########################################################################################

# IMPORT EXTERNAL LIBRARIES

import numpy as np
from copy import copy
from nltk.metrics import edit_distance

#########################################################################################

def euclidean_distance(human_scanpath: np.ndarray,
                      simulated_scanpath: np.ndarray) -> np.ndarray | bool:
    """
    Compute Euclidean distance between corresponding fixations in two scanpaths.

    Parameters
    ----------
    human_scanpath : np.ndarray
        First scanpath as (n, 2) array of (x, y) coordinates
    simulated_scanpath : np.ndarray
        Second scanpath as (n, 2) array of (x, y) coordinates

    Returns
    -------
    np.ndarray or bool
        Array of distances for each fixation pair, or False if lengths don't match
    """
    if len(human_scanpath) == len(simulated_scanpath):
        distances = np.zeros(len(human_scanpath))
        for i in range(len(human_scanpath)):
            p = human_scanpath[i]
            q = simulated_scanpath[i]
            distances[i] = np.sqrt((p[0] - q[0])**2 + (p[1] - q[1])**2)
        return distances
    else:
        print('Error: The two sequences must have the same length!')
        return False


def scanpath_to_string(scanpath: np.ndarray, stimulus_width: int,
                      stimulus_height: int, grid_size: int) -> str:
    """
    Convert scanpath to string representation by dividing image into grid.

    Parameters
    ----------
    scanpath : np.ndarray
        Scanpath as (n, 2) array of (x, y) coordinates
    stimulus_width : int
        Width of the stimulus image
    stimulus_height : int
        Height of the stimulus image
    grid_size : int
        Size of the grid (grid_size x grid_size)

    Returns
    -------
    str
        String representation of the scanpath
    """
    width_step = stimulus_width // grid_size
    height_step = stimulus_height // grid_size

    string_parts = []
    for fixation in scanpath.astype(np.int32):
        grid_x = fixation[0] // width_step
        grid_y = fixation[1] // height_step
        grid_pos = grid_x + grid_y * grid_size
        string_parts.append(chr(97 + int(grid_pos)))  # 'a' + position

    return ''.join(string_parts)


def string_edit_distance(scanpath_1: np.ndarray, scanpath_2: np.ndarray,
                        stimulus_width: int, stimulus_height: int,
                        grid_size: int = 4) -> tuple[float, str, str]:
    """
    Compute string edit distance between two scanpaths.

    Converts scanpaths to strings using spatial grid, then computes
    Levenshtein distance between the strings.

    Parameters
    ----------
    scanpath_1, scanpath_2 : np.ndarray
        Scanpaths as (n, 2) arrays
    stimulus_width, stimulus_height : int
        Dimensions of the stimulus
    grid_size : int, default=4
        Grid size for string conversion

    Returns
    -------
    tuple[float, str, str]
        (distance, string1, string2)
    """
    string_1 = scanpath_to_string(scanpath_1, stimulus_width, stimulus_height, grid_size)
    string_2 = scanpath_to_string(scanpath_2, stimulus_width, stimulus_height, grid_size)

    distance = edit_distance(string_1, string_2, transpositions=True)
    return distance, string_1, string_2


def time_delay_embedding_distance(human_scanpath: np.ndarray,
                                 simulated_scanpath: np.ndarray,
                                 k: int = 3,
                                 distance_mode: str = 'Mean') -> float | bool:
    """
    Compute time-delay embedding distance between scanpaths.

    Based on Wang et al. (2011) - uses time-delay embeddings to compare
    scanpaths of different lengths.

    Parameters
    ----------
    human_scanpath, simulated_scanpath : np.ndarray
        Scanpaths as (n, 2) arrays
    k : int, default=3
        Time-embedding vector dimension
    distance_mode : str, default='Mean'
        'Mean' or 'Hausdorff'

    Returns
    -------
    float or bool
        Distance score, or False on error
    """
    if len(human_scanpath) < k or len(simulated_scanpath) < k:
        print('ERROR: Too large value for the time-embedding vector dimension')
        return False

    # Create time-embedding vectors
    human_vectors = [human_scanpath[i:i + k] for i in range(len(human_scanpath) - k + 1)]
    simulated_vectors = [simulated_scanpath[i:i + k] for i in range(len(simulated_scanpath) - k + 1)]

    distances = []
    for sim_vec in simulated_vectors:
        # Find minimum distance to any human vector
        norms = [np.linalg.norm(euclidean_distance(sim_vec, hum_vec))
                for hum_vec in human_vectors]
        distances.append(min(norms) / k)

    if distance_mode == 'Mean':
        return sum(distances) / len(distances)
    elif distance_mode == 'Hausdorff':
        return max(distances)
    else:
        print('ERROR: distance mode not defined.')
        return False


def scaled_time_delay_embedding_distance(human_scanpath: np.ndarray,
                                        simulated_scanpath: np.ndarray,
                                        image: np.ndarray,
                                        to_plot: bool = False) -> float:
    """
    Compute scaled time-delay embedding distance.

    Scales coordinates to [0,1] range and computes similarity across all k values.

    Parameters
    ----------
    human_scanpath, simulated_scanpath : np.ndarray
        Scanpaths as (n, 2) arrays
    image : np.ndarray
        Stimulus image for scaling
    to_plot : bool, default=False
        Whether to plot similarities vs k

    Returns
    -------
    float
        Mean similarity across all k values
    """
    # Work on copies
    h_scanpath = copy(human_scanpath)
    s_scanpath = copy(simulated_scanpath)

    # Scale coordinates to [0,1]
    max_dim = float(max(image.shape))
    for fixation in h_scanpath:
        fixation[0] /= max_dim
        fixation[1] /= max_dim
    for fixation in s_scanpath:
        fixation[0] /= max_dim
        fixation[1] /= max_dim

    # Compute similarities for all possible k
    max_k = min(len(h_scanpath), len(s_scanpath))
    similarities = []
    for k in range(1, max_k + 1):
        distance = time_delay_embedding_distance(h_scanpath, s_scanpath, k=k)
        if distance is not False:
            similarities.append(np.exp(-distance))

    if to_plot:
        import matplotlib.pyplot as plt

        plt.plot(range(1, max_k + 1), similarities)
        plt.xlabel('k (embedding dimension)')
        plt.ylabel('Similarity')
        plt.show()

    return sum(similarities) / len(similarities) if similarities else 0.0


def string_based_time_delay_embedding_distance(scanpath_1: np.ndarray,
                                              scanpath_2: np.ndarray,
                                              stimulus_width: int,
                                              stimulus_height: int,
                                              k: int = 3,
                                              distance_mode: str = 'Mean') -> float | bool:
    """
    Compute string-based time-delay embedding distance.

    Converts scanpaths to strings, then applies time-delay embedding in string space.

    Parameters
    ----------
    scanpath_1, scanpath_2 : np.ndarray
        Scanpaths as (n, 2) arrays
    stimulus_width, stimulus_height : int
        Stimulus dimensions
    k : int, default=3
        Embedding dimension
    distance_mode : str, default='Mean'
        'Mean' or 'Hausdorff'

    Returns
    -------
    float or bool
        Distance score, or False on error
    """
    if len(scanpath_1) < k or len(scanpath_2) < k:
        print('ERROR: Too large value for the time-embedding vector dimension')
        return False

    # Create time-embedding vectors
    vectors_1 = [scanpath_1[i:i + k] for i in range(len(scanpath_1) - k + 1)]
    vectors_2 = [scanpath_2[i:i + k] for i in range(len(scanpath_2) - k + 1)]

    distances = []
    for vec_2 in vectors_2:
        # Find minimum string edit distance to any vector from scanpath_1
        norms = []
        for vec_1 in vectors_1:
            dist, _, _ = string_edit_distance(vec_1, vec_2, stimulus_width, stimulus_height)
            norms.append(dist)
        distances.append(min(norms) / k)

    if distance_mode == 'Mean':
        return sum(distances) / len(distances)
    elif distance_mode == 'Hausdorff':
        return max(distances)
    else:
        print('ERROR: distance mode not defined.')
        return False


def compute_rqa_metrics(scanpath_1: np.ndarray, scanpath_2: np.ndarray,
                       r: float = 60, ll: int = 2) -> tuple:
    """
    Compute Recurrence Quantification Analysis (RQA) metrics.

    Based on Anderson et al. (2015).

    Parameters
    ----------
    scanpath_1, scanpath_2 : np.ndarray
        Scanpaths as (n, 2) arrays
    r : float, default=60
        Radius threshold
    ll : int, default=2
        Minimum line length

    Returns
    -------
    tuple
        (determinism, laminarity, center_of_recurrence_mass, cross_recurrence)
    """
    from .rqa import RQA

    # Extract x,y coordinates only
    if scanpath_1.shape[1] > 2:
        sp1 = scanpath_1[:, :2]
    else:
        sp1 = scanpath_1

    if scanpath_2.shape[1] > 2:
        sp2 = scanpath_2[:, :2]
    else:
        sp2 = scanpath_2

    rqa_obj = RQA(sp1, sp2)

    determinism = rqa_obj.determinism()
    laminarity = rqa_obj.laminarity()
    corm = rqa_obj.centerrecmass()
    crossrec = rqa_obj.crossrec()

    return determinism, laminarity, corm, crossrec


def scanmatch_metric(scanpath_1: np.ndarray, scanpath_2: np.ndarray,
                    stimulus_width: int, stimulus_height: int,
                    x_bins: int = 14, y_bins: int = 8, temp_bins: int = 50) -> float:
    """
    Compute ScanMatch similarity score.

    Based on Cristino et al. (2010).

    Parameters
    ----------
    scanpath_1, scanpath_2 : np.ndarray
        Scanpaths as (n, 2) or (n, 4) arrays
    stimulus_width, stimulus_height : int
        Stimulus dimensions
    x_bins, y_bins : int
        Spatial binning parameters
    temp_bins : int
        Temporal binning parameter

    Returns
    -------
    float
        Similarity score
    """
    from .scanmatch import ScanMatch

    # Handle different input formats
    if scanpath_1.shape[1] > 2 and scanpath_2.shape[1] > 2:
        # Convert timing to milliseconds
        diff1 = (scanpath_1[:, 3] - scanpath_1[:, 2]) * 1000.
        sp1 = np.hstack([scanpath_1[:, :2], diff1.reshape(-1, 1)])
        diff2 = (scanpath_2[:, 3] - scanpath_2[:, 2]) * 1000.
        sp2 = np.hstack([scanpath_2[:, :2], diff2.reshape(-1, 1)])
        temp_bins = temp_bins
    elif scanpath_1.shape[1] == 2 and scanpath_2.shape[1] == 2:
        sp1, sp2 = scanpath_1, scanpath_2
        temp_bins = 0.0
    else:
        raise ValueError("Scanpaths should be arrays of shape [nfix,2] or [nfix,4]!")

    match_obj = ScanMatch(Xres=stimulus_width, Yres=stimulus_height,
                         Xbin=x_bins, Ybin=y_bins, TempBin=temp_bins)
    seq1 = match_obj.fixationToSequence(sp1).astype(int)
    seq2 = match_obj.fixationToSequence(sp2).astype(int)

    score, _, _ = match_obj.match(seq1, seq2)
    return score


def multimatch_metric(scanpath_1: np.ndarray, scanpath_2: np.ndarray,
                     stimulus_width: int, stimulus_height: int) -> dict:
    """
    Compute MultiMatch similarity scores.

    Based on Jarodzka et al. (2010).

    Parameters
    ----------
    scanpath_1, scanpath_2 : np.ndarray
        Scanpaths as (n, 4) arrays with timing
    stimulus_width, stimulus_height : int
        Stimulus dimensions

    Returns
    -------
    dict
        MultiMatch similarity scores
    """
    try:
        import multimatch as mmg
    except ImportError:
        raise ImportError("multimatch package is required. Install with: pip install multimatch")

    if scanpath_1.shape[1] <= 2 or scanpath_2.shape[1] <= 2:
        raise ValueError("Scanpaths should be arrays of shape [nfix,4] with timing data!")

    # Convert timing to milliseconds
    diff1 = (scanpath_1[:, 3] - scanpath_1[:, 2]) * 1000.
    sp1 = np.hstack([scanpath_1[:, :2], diff1.reshape(-1, 1)])
    diff2 = (scanpath_2[:, 3] - scanpath_2[:, 2]) * 1000.
    sp2 = np.hstack([scanpath_2[:, :2], diff2.reshape(-1, 1)])

    # Convert to records for multimatch
    import pandas as pd
    scan1_df = pd.DataFrame({'start_x': sp1[:, 0], 'start_y': sp1[:, 1], 'duration': sp1[:, 2]})
    scan2_df = pd.DataFrame({'start_x': sp2[:, 0], 'start_y': sp2[:, 1], 'duration': sp2[:, 2]})

    scores = mmg.docomparison(scan1_df.to_records(), scan2_df.to_records(),
                             screensize=[stimulus_width, stimulus_height])
