from typing import List


def shingleset_k(s: str, k: int) -> set:
    shingles = []
    q = len(s)
    for n in range(1, k + 1):
        shingles.append(set([s[i:(i + n)] for i in range(q - n + 1)]))
    return set.union(*shingles)


def shingleset_range(s: str, n_min: int, n_max: int) -> set:
    # correct wrong inputs
    n_max_ = max(0, n_max)
    n_min_ = max(1, n_min)
    # start to loop
    shingles = []
    q = len(s)
    for n in range(n_min_, n_max_ + 1):
        shingles.append(set([s[i:(i + n)] for i in range(q - n + 1)]))
    return set.union(*shingles)


def shingleset_list(s: str, klist: List[int]) -> set:
    shingles = []
    q = len(s)
    for n in klist:
        if n > 0:
            shingles.append(set([s[i:(i + n)] for i in range(q - n + 1)]))
    return set.union(*shingles)
