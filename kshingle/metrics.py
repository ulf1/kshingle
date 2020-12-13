from typing import Optional
from .shingleset import shingleset_k
from .wildcard import wildcard_shinglesets


def jaccard(A: set, B: set) -> float:
    u = float(len(A.intersection(B)))
    return u / (len(A) + len(B) - u)


def jaccard_strings(s1: str, s2: str,
                    k: Optional[int] = 1,
                    n_max_wildcards: Optional[int] = None
                    ) -> float:
    # limit k to the shortest str len
    k_max = min(k, len(s1), len(s2))
    # Shingling
    A = shingleset_k(s1, k_max)
    B = shingleset_k(s2, k_max)
    # Wildcard characters
    if n_max_wildcards:
        A = A.union(wildcard_shinglesets(A, n_max_wildcards))
        B = B.union(wildcard_shinglesets(B, n_max_wildcards))
    # compute similarity
    return jaccard(set(A), set(B))
