from typing import Dict, Optional, Union, List
from .cews import sort_by_memostats
import re
import itertools
import numpy as np
from shingleseqs import shingleseqs_k


def shingles_to_patterns(memo: Dict[str, int],
                         wildcard: Optional[str] = '\uFFFF'
                         ):  # -> Dict[int, List[re.Pattern]]:
    """Convert shingles with wildcards to regex patterns

    Parameters:
    -----------
    memo: dict
        Database for memoization, i.e. `memo[shingle]=count`. In case of the
          wildcarded shingle, the residual counts that are not covered by the
          selected set of shingles (Basically the `1 - p`).
        The keys in the memoization cache are selected shingles of the CEWS
          algorithm.

    wildcard : str
        An unicode char that is not actually used by any natural language,
          or the text that you analyzing, e.g. U+FFFE or U+FFFF
          See https://en.wikipedia.org/wiki/Specials_(Unicode_block)

    Returns:
    --------
    PATTERNS : Dict[int, List[re.Pattern]]
        The regex.compile patterns based on the selected shingles in the
          memoization cache.
    """
    # sort memo cache
    if isinstance(memo, dict):
        MEMOSTATS = [(
            s, len(s.split(wildcard)) - 1, len(s[1:-1].split(wildcard)) - 1,
            len(s), c) for s, c in memo.items()]
    elif isinstance(memo, (list, tuple)):
        MEMOSTATS = [(
            s, len(s.split(wildcard)) - 1, len(s[1:-1].split(wildcard)) - 1,
            len(s), 0) for s in memo]
    MEMOSTATS.sort(key=sort_by_memostats)
    shingles = [x[0] for x in MEMOSTATS]
    # convert shingles to regex patterns
    PATTERNS = {}
    for shingle in shingles:
        # create sublist
        n = len(shingle)
        if PATTERNS.get(n) is None:
            PATTERNS[n] = []
        # create regex
        reg = r"\w{1}".join([re.escape(s) for s in shingle.split(wildcard)])
        pat = re.compile(f"^{reg}$")
        PATTERNS[n].append(pat)
    return PATTERNS


def encode_with_patterns(x: Union[list, str],
                         PATTERNS: dict,  # Dict[int, List[re.Pattern]],
                         unkid: Optional[int] = None):
    """Encode all elements of x with the regex pattern.

    Parameters:
    -----------
    x : Union[list, str]
        Encoding happens if type(x)==str. If type(x)=list then a recursive
          call on each list element is triggered.

    PATTERNS : Dict[int, List[re.Pattern]]
        The regex.compile patterns based on the selected shingles in the
          memoization cache.

    unkid : int
        Index of the UKNOWN token (UNK). It's `unkid=len(PATTERNS)` by default

    Returns:
    --------
    encoded : Union[list, int]
        The IDs refer to the position index in PATTERNS list
    """
    if isinstance(x, str):
        nx = len(x)
        n_pat = len(PATTERNS.get(nx, []))
        for i in range(n_pat):
            if PATTERNS[nx][i].match(x):
                return i
        return unkid if unkid else n_pat
    else:
        return [encode_with_patterns(el, PATTERNS, unkid) for el in x]


def encode_multi_match_str(x: str,
                           PATTERNS: dict,  # Dict[int, List[re.Pattern]],
                           num_matches: Optional[int] = 1,
                           unkid: Optional[int] = None):
    """ Encode 1 shingle for `encode_multi_match_corpus` """
    nx = len(x)
    out = []
    for i, pat in enumerate(PATTERNS.get(nx, [])):
        if pat.match(x):
            out.append(i)
            if len(out) >= num_matches:
                break
    # fill empty list elements
    for _ in range(num_matches - len(out)):
        out.append(unkid)
    return out


def encode_multi_match_corpus(corpus: List[str],
                              k: int,
                              PATTERNS: list,  # Dict[int, List[re.Pattern]],
                              num_matches: Optional[int] = 1,
                              unkid: Optional[int] = None,
                              stack: bool = True):
    """ Shingle and encode corpus

    Example:
    --------
    corpus = ["lenghty text.", "another long article"]
    encoded, shingled = encode_multi_match_corpus(
        corpus, k=k, PATTERNS=PATTERNS, num_matches=3, stack=True)
    """
    # generate all shingles (docs, k, seqlen)
    shingled = [
        shingleseqs_k(doc, k=k, padding='post', placeholder="[PAD]")
        for doc in corpus]

    # transpose (docs, seqlen, k)
    shingled = [
        np.array(shingled_doc, dtype=object).T.tolist()
        for shingled_doc in shingled]

    # encode (docs, seqlen, k)
    encoded = [
        [[encode_multi_match_str(
            ksegment,
            PATTERNS=PATTERNS,
            num_matches=min(nk + 1, num_matches),
            unkid=unkid)
          for nk, ksegment in enumerate(seq)]
         for seq in doc]
        for doc in shingled
    ]

    # flatten (docs, seqlen, k, num) to (docs, seqlen, k*num)
    encoded = [
        [list(itertools.chain(*seq)) for seq in doc]
        for doc in encoded]

    # merge to one big sequence
    if stack:
        encoded = np.vstack(encoded)

    # done
    return encoded, shingled
