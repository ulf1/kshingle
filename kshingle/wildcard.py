from typing import List, Set
import itertools


def replace_with_wildcard(word: str, indices: List[int],
                          wildcard: str = '\uFFFF'):
    """Replace char at a certain index with a wildcard

    word : str
        A string

    indices : List[int]
        List of indicies. len(word)<max(indices)

    wildcard : str
        An unicode char that is not actually used by any natural language,
          or the text that you analyzing, e.g. U+FFFE or U+FFFF
          See https://en.wikipedia.org/wiki/Specials_(Unicode_block)

    Example:
    --------
        word = 'ABCDE'
        replace_with_wildcard(s, [2, 4])
    """
    return ''.join([wildcard if i in indices else c
                    for i, c in enumerate(word)])


def get_wildcard_variants(word: str,
                          n_max_wildcards: int = None,
                          wildcard: str = '\uFFFF') -> List[str]:
    """Generate all wildcard variants for one word

    word : str
        A string

    n_max_wildcards : int
        Maximum number of wildcard characters per word.

    wildcard : str
        An unicode char that is not actually used by any natural language,
          or the text that you analyzing, e.g. U+FFFE or U+FFFF
          See https://en.wikipedia.org/wiki/Specials_(Unicode_block)
    """
    # Set the maximum number of number of wildcards for our word
    if n_max_wildcards is None:
        n_wild = len(word) - 1
    else:
        n_wild = min(len(word) - 1, n_max_wildcards)

    # pre-specify the word's indicies from which we draw combinations
    availidx = list(range(len(word)))

    # start loop
    variants = []
    for w in range(1, n_wild + 1):
        for indices in list(itertools.combinations(availidx, w)):
            variants.append(replace_with_wildcard(
                word, indices=indices, wildcard=wildcard))
    # done
    return variants


def wildcard_shinglesets(words: List[str],
                         n_max_wildcards: int = None,
                         wildcard: str = '\uFFFF') -> Set[str]:
    """Generate wildcard variants for each word

    word : str
        A string

    n_max_wildcards : int
        Maximum number of wildcard characters per word.

    wildcard : str
        An unicode char that is not actually used by any natural language,
          or the text that you analyzing, e.g. U+FFFE or U+FFFF
          See https://en.wikipedia.org/wiki/Specials_(Unicode_block)

    Example:
    --------
        import kshingle as ks
        shingles = ks.shingleset_k("aBc DeF", k=5)
        shingles = shingles.union(
            ks.wildcard_shinglesets(shingles, n_max_wildcards=2))
    """
    tmp = []
    for word in words:
        tmp.extend(get_wildcard_variants(word, n_max_wildcards, wildcard))
    return set(tmp)
