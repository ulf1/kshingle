import ray
import psutil
from .cews import expandshingle
from typing import Optional, Dict, Union, List
import numpy as np
import re


@ray.remote
def ray_expandshingle(s: str,
                      db: Dict[str, int],
                      memo: Optional[dict],
                      wildcard: Optional[str] = '\uFFFF',
                      max_wildcards: Optional[int] = 1,
                      min_samples_split: Optional[int] = 2,
                      min_samples_leaf: Optional[int] = 1,
                      threshold: Optional[float] = 0.8):
    """ Ray.io wrapper for ks.expandshingle """
    return expandshingle(
        s, db=db, memo=memo,
        wildcard=wildcard,
        max_wildcards=max_wildcards,
        min_samples_split=min_samples_split,
        min_samples_leaf=min_samples_leaf,
        threshold=threshold)


def cews_cpu(db: Dict[str, int],
             memo: Optional[dict] = {},
             wildcard: Optional[str] = '\uFFFF',
             max_wildcards: Optional[int] = 1,
             min_samples_split: Optional[int] = None,
             min_samples_leaf: Optional[int] = 1,
             threshold: Optional[float] = 0.8,
             priority: Optional[str] = 'common',
             vocab_size: Optional[int] = None):
    # Start ray.io
    NUM_CPUS = max(1, int(psutil.cpu_count(logical=True) * 0.9))
    ray.init(num_cpus=NUM_CPUS)
    print(f"Num CPUs: {NUM_CPUS}")

    # add single-chars to memo automatically
    if len(memo) == 0:
        memo = {k: v for k, v in db.items() if len(k) == 1}

    # sort shingles by frequency
    db_list = list(db.items())
    db_list = sorted(db_list, key=lambda item: -item[1])

    # approximate `min_samples_leaf` with `vocab_size`
    if (min_samples_leaf == 'auto') and (vocab_size is not None):
        idx = min(len(db_list) - 1, vocab_size)
        min_samples_leaf = int(max(1, db_list[idx][1]))

    # if `min_samples_leaf` is float
    if isinstance(min_samples_leaf, float) and (0.0 < min_samples_leaf <= 1.0):
        cnts = np.array([c for _, c in db_list])
        mask = (cnts / np.sum(cnts)) > min_samples_leaf
        if mask.any():
            min_samples_leaf = int(cnts[mask][-1])
        else:
            min_samples_leaf = 1

    # check threshold
    assert threshold is not None
    assert (0.0 < threshold <= 1.0)

    # set `min_samples_split`
    if min_samples_split is None:
        min_samples_split = max(2, int(min_samples_leaf / threshold))

    # only shingles with at least `min_samples_leaf` counts
    if priority == 'rare':
        shingles = [s for s, _ in db_list]
        shingles.reverse()
    elif (priority == 'common') and (vocab_size is not None):
        shingles = [s for s, c in db_list if c >= min_samples_leaf]
    else:  # priority == 'common'
        shingles = [s for s, _ in db_list]

    # start parallel searches
    for start in range(0, len(shingles), NUM_CPUS):
        # run trees in parallel
        tmp_memos = []
        for s in shingles[start:(start + NUM_CPUS)]:
            tmp_memos.append(ray_expandshingle.remote(
                s, db=db, memo=memo,
                wildcard=wildcard,
                max_wildcards=max_wildcards,
                min_samples_split=min_samples_split,
                min_samples_leaf=min_samples_leaf,
                threshold=threshold))
        # collect results
        tmp_memos = ray.get(tmp_memos)
        for m in tmp_memos:
            memo.update(m)
        # early stopping
        if vocab_size is not None:
            if len(memo) >= vocab_size:
                break

    # stop ray
    ray.shutdown()
    # done
    return memo


@ray.remote
def encode_with_patterns_recur(x: Union[list, str],
                               PATTERNS: dict,  # Dict[int, List[re.Pattern]],
                               unkid: Optional[int] = None):
    if isinstance(x, str):
        nx = len(x)
        n_pat = len(PATTERNS.get(nx, []))
        for i in range(n_pat):
            if PATTERNS[nx][i].match(x):
                return i
        return unkid if unkid else n_pat
    else:
        tmp = []
        for element in x:
            tmp.append(encode_with_patterns_recur.remote(
                element, PATTERNS, unkid))
        return ray.get(tmp)


def encode_with_patterns_cpu(x: Union[list, str],
                             PATTERNS: dict,  # Dict[int, List[re.Pattern]],
                             unkid: Optional[int] = None):
    """Encode all elements of x with the regex pattern.

    Parameters:
    -----------
    x : Union[list, str]
        Encoding happens if type(x)==str. If type(x)=list then a recursive
          call on each list element is triggered.

    PATTERNS : List[re.Pattern]
        The regex.compile patterns based on the selected shingles in the
          memoization cache.

    unkid : int
        Index of the UKNOWN token (UNK). It's `unkid=len(PATTERNS)` by default

    Returns:
    --------
    encoded : Union[list, int]
        The IDs refer to the position index in PATTERNS list
    """
    # Start ray.io
    NUM_CPUS = max(1, int(psutil.cpu_count(logical=True) * 0.9))
    ray.init(num_cpus=NUM_CPUS)
    print(f"Num CPUs: {NUM_CPUS}")
    # encode
    encoded = ray.get(encode_with_patterns_recur.remote(x, PATTERNS, unkid))
    # stop ray
    ray.shutdown()
    # done
    return encoded
