import ray
import psutil
import random
from .cews import expandshingle
from typing import Optional, Dict
import numpy as np


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
             min_samples_split: Optional[int] = 2,
             min_samples_leaf: Optional[int] = 1,
             threshold: Optional[float] = 0.8,
             approx_vocab_size: Optional[int] = None):
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

    # approximate `min_samples_leaf` with `approx_vocab_size`
    if approx_vocab_size:
        idx = min(len(db_list) - 1, approx_vocab_size)
        min_samples_leaf = int(max(1, db_list[idx][1]))
        min_samples_split = int(2 * min_samples_leaf)

    # if `min_samples_leaf` is float
    if isinstance(min_samples_leaf, float) and (0.0 < min_samples_leaf <= 1.0):
        cnts = np.array([c for _, c in db_list])
        mask = (cnts / np.sum(cnts)) > min_samples_leaf
        if mask.any():
            min_samples_leaf = int(cnts[mask][-1])
            min_samples_split = int(2 * min_samples_leaf)
        else:
            min_samples_leaf, min_samples_split = 1, 2

    # only shingles with at least `min_samples_leaf` counts
    shingles = [s for s, c in db_list if c >= min_samples_leaf]
    # shingles = [s for s, _ in db_list]

    # start parallel searches
    for start in range(0, len(shingles), NUM_CPUS):
        tmp_memos = []
        for s in shingles[start:(start + NUM_CPUS)]:
            tmp_memos.append(ray_expandshingle.remote(
                s, db=db, memo=memo, 
                wildcard=wildcard,
                max_wildcards=max_wildcards,
                min_samples_split=min_samples_split,
                min_samples_leaf=min_samples_leaf,
                threshold=threshold))
        tmp_memos = ray.get(tmp_memos)
        for m in tmp_memos:
            memo.update(m)
    # stop ray
    ray.shutdown()
    # done
    return memo
