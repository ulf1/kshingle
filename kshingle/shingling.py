from typing import List
import numba


@numba.jit(nopython=True)
def shingling_k(s: str, k: int) -> List[List[str]]:
    """Convert a string to a list of k sequences with k-shingles

    Parameters:
    -----------
    s: str
        The raw string

    k: int
        The parameter must be k>=1

    Returns:
    --------
    List[List[str]]
        A list of k sequences. The 1st sublist contains the chars of the
          string s, e.g. ['a', 'b', 'c'] for s="abc". The k=2 list containd
          2-shingles, e.g. ['ab', 'bc'].

    Example:
    --------
        import kshingle as ks
        shingles = ks.shingling_k("abc", k=2)
    """
    shingles = []
    q = len(s)
    for n in range(1, k + 1):
        shingles.append([s[i:(i + n)] for i in range(q - n + 1)])
    return shingles


@numba.jit(nopython=True)
def shingling_range(s: str, n_min: int, n_max: int) -> List[List[str]]:
    """Convert a string to a list of k sequences with k-shingles

    Parameters:
    -----------
    s: str
        The raw string

    n_min: int
        The lower bound k range [n_min, n_max]

    n_max: int
        The upper bound of the k range [n_min, n_max]

    Returns:
    --------
    List[List[str]]
        A list of k sequences. The k=1 sublist contains the chars of the
          string s, e.g. ['a', 'b', 'c', 'd'] for s="abcd". The k=3 list
          contains 3-shingles, e.g. ['abc', 'bcd'].

    Example:
    --------
        import kshingle as ks
        shingles = ks.shingling_range("abcd", [2, 3])
    """
    # correct wrong inputs
    n_max_ = max(0, n_max)
    n_min_ = max(1, n_min)
    # start to loop
    shingles = []
    q = len(s)
    for n in range(n_min_, n_max_ + 1):
        shingles.append([s[i:(i + n)] for i in range(q - n + 1)])
    return shingles


def shingling_list(s: str, klist: List[int]) -> List[List[str]]:
    """Convert a string to a list of k sequences with k-shingles

    Parameters:
    -----------
    s: str
        The raw string

    klist: List[int]
        A list of specific k values, e.g. klist=[1, 3, 6]

    Returns:
    --------
    List[List[str]]
        A list of k sequences. The k=1 sublist contains the chars of the
          string s, e.g. ['a', 'b', 'c', 'd'] for s="abcd". The k=3 list
          contains 3-shingles, e.g. ['abc', 'bcd'].

    Example:
    --------
        import kshingle as ks
        shingles = ks.shingling_list("abcd", klist=[1, 3])
    """
    return shingling_list_numba(s, numba.typed.List(klist))


@numba.jit(nopython=True)
def shingling_list_numba(s: str,
                         klist: numba.typed.List
                         ) -> List[List[str]]:
    shingles = []
    q = len(s)
    for n in klist:
        if n > 0:
            shingles.append([s[i:(i + n)] for i in range(q - n + 1)])
    return shingles
