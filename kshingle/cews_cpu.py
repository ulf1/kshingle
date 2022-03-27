import ray
import psutil
import random
from .cews import expandshingle
from typing import Optional, Dict


@ray.remote
def ray_expandshingle(s: str,
                      db: Dict[str, int],
                      memo: Optional[dict],
                      wildcard: Optional[str] = '\uFFFF',
                      threshold: Optional[float] = 0.8,
                      min_count_split: Optional[int] = 2,
                      max_wildcards: Optional[int] = 3):
    """ Ray.io wrapper for ks.expandshingle """
    return expandshingle(
        s, db=db, memo=memo, wildcard=wildcard, threshold=threshold,
        min_count_split=min_count_split, max_wildcards=max_wildcards)


def cews_cpu(db: Dict[str, int],
             memo: Optional[dict] = {},
             wildcard: Optional[str] = '\uFFFF',
             threshold: Optional[float] = 0.8,
             min_count_split: Optional[int] = 2,
             max_wildcards: Optional[int] = 3):
    # Start ray.io
    NUM_CPUS = max(1, int(psutil.cpu_count(logical=True) * 0.9))
    ray.init(num_cpus=NUM_CPUS)
    print(f"Num CPUs: {NUM_CPUS}")

    # add single-chars to memo automatically
    if len(memo) == 0:
        memo = {k: v for k, v in db.items() if len(k) == 1}

    # random order of the shingles
    shingles = list(db.keys())
    random.seed(42)
    random.shuffle(shingles)

    # start parallel searches
    for start in range(0, len(shingles), NUM_CPUS):
        tmp_memos = []
        for s in shingles[start:(start + NUM_CPUS)]:
            tmp_memos.append(ray_expandshingle.remote(
                s, db=db, memo=memo, wildcard=wildcard, threshold=threshold,
                min_count_split=min_count_split, max_wildcards=max_wildcards))
        tmp_memos = ray.get(tmp_memos)
        for m in tmp_memos:
            memo.update(m)
    # stop ray
    ray.shutdown()
    # done
    return memo
