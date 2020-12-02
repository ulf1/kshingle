from typing import List


def shingleset_k(s: str, k: int) -> set:
    shingles = []
    q = len(s)
    for n in range(1, k + 1):
        shingles.append(set([s[i:(i + n)] for i in range(q - n + 1)]))
    return set.union(*shingles)
