from typing import List, Optional, Union
import functools
import itertools
import collections
import math
import warnings


def identify_vocab(shingled: List[List[str]],
                   sortmode: Optional[str] = 'most-common',
                   n_min_count: Optional[int] = 1,
                   n_max_vocab: Optional[int] = None
                   ) -> List[str]:
    """Count unique shingles, exclude rare shingles (n_min_count), and/or
        select the N most frequent shingles (n_max_vocab)

    shingled : List[List[str]]
        A list of lists of shingles.

    sortmode : Optional[str]
        Type of sorting. Default: 'most-common'
        - 'most-common' -- Pick the most frequent shingles
        - 'prefer-shorter' -- Most frequent. Prefer short str for same freq.
        - 'times-length' -- Sort by "frequency * len(shingle)"
        - 'sqrt-x-length' -- Sort by "sqrt(frequency) * len(shingle)"
        - 'log-x-length' -- Sort by "log(1 + frequency) * len(shingle)"

    n_min_count : Optional[int]
        Only consider shingles that occurs at least M times in the corpus

    n_max_vocab : Optional[int]
        Return the N most frequent shingles as vocabulary

    Return:
    -------
    List[str]
        Vocabulary list of shingles

    Example:
    --------
        import kshingle as ks
        data = ['abc d abc de abc def', 'abc defg abc def gh abc def ghi']
        shingled = [ks.shingling_k(s, k=9) for s in data]
        VOCAB = ks.identify_vocab(
            shingled, sortmode='times-length', n_min_count=2, n_max_vocab=10)
        print(VOCAB)
    """
    # count all strings
    cnt = functools.reduce(
        lambda x, y: x + collections.Counter(itertools.chain(*y)),
        shingled, collections.Counter([]))

    # sort by fn(frequency, prop(shingle))
    if sortmode == 'prefer-shorter':
        cnt = sorted(
            cnt.items(), reverse=True,
            key=lambda x: (x[1], -len(x[0])))
    elif sortmode == 'times-length':
        cnt = sorted(
            cnt.items(), reverse=True,
            key=lambda x: (x[1] * len(x[0]), x[1], -len(x[0])))
    elif sortmode == 'sqrt-x-length':
        cnt = sorted(
            cnt.items(), reverse=True,
            key=lambda x: (math.sqrt(x[1]) * len(x[0]), x[1], -len(x[0])))
    elif sortmode == 'log-x-length':
        cnt = sorted(
            cnt.items(), reverse=True,
            key=lambda x: (math.log(1 + x[1]) * len(x[0]), x[1], -len(x[0])))
    else:  # 'most-common'
        cnt = cnt.most_common()

    # filter by counts
    tmp = n_min_count if n_min_count else 0
    voc = [key for key, val in cnt if val >= tmp]

    # limit number of distinct shingles
    if n_max_vocab:
        voc = voc[:n_max_vocab]

    return voc


def upsert_word_to_vocab(VOCAB: List[str], word: str) -> (List[str], int):
    """Upsert a word to to vocabulary, and return new vocabulary list
        as well as the word's index

    VOCAB : List[str]
        vocabulary list

    word : str
        new to word to insert, or existing word word to lookup

    Return:
    -------
    List[str]
        Upldated VOCAB

    int
        Index of word

    Example:
    --------
        import kshingle as ks
        VOCAB = ['a', 'b']
        VOCAB, idx = ks.upsert_word_to_vocab(VOCAB, "[UNK]")
        print(idx, VOCAB)
    """
    try:
        idx = VOCAB.index(word)
    except Exception:
        VOCAB.append(word)
        idx = VOCAB.index(word)
    return VOCAB, idx


def encode_with_vocab(x: Union[list, str],
                      VOCAB: List[str],
                      unkid: int) -> Union[list, int]:
    """Encode all elements of x that are strings.

    x: Union[list, str]
        Encoding happens if type(x)==str. If type(x)=list then a recursive
          call on each list element is triggered.

    VOCAB : List[str]
        vocabulary list

    unkid : int
        Index of the UKNOWN token, e.g. unkid=VOCAB.index("[UNK]")

    Returns:
    --------
    Union[list, int]
        The final result (after all recursions) has the same structure as x
          but with integer encoded elements.

    Example:
    --------
        import kshingle as ks
        data = ['abc d abc de abc def', 'abc defg abc def gh abc def ghi']
        shingled = [ks.shingling_k(s, k=9) for s in data]
        VOCAB = ks.identify_vocab(shingled, n_max_vocab=10)
        VOCAB, unkid = ks.upsert_word_to_vocab(VOCAB, "[UNK]")
        encoded = ks.encode_with_vocab(shingled, VOCAB, unkid)
    """
    if isinstance(x, str):
        try:
            return VOCAB.index(x)
        except Exception:
            return unkid
    else:
        return [encode_with_vocab(e, VOCAB, unkid) for e in x]


def shrink_k_backwards(encoded: List[List[int]], unkid: int) -> List[int]:
    """Find k-th sequences that only contain UNKIDs to exclude them. Return
        a list of k's that contain at least one encoded shingle across
        all examples.

    encoded: List[List[int]]

    unkid : int
        Index of the UKNOWN token, e.g. unkid=VOCAB.index("[UNK]")

    Return:
    -------
    klist : List[int]
        A list of k's that contain at least one encoded shingle across
          all examples.

    Example:
    --------
        import kshingle as ks
        data = ['abc d abc de abc def', 'abc defg abc def gh abc def ghi']
        # Step 1: Build a VOCAB
        shingled = [ks.shingling_k(s, k=9) for s in data]
        VOCAB = ks.identify_vocab(shingled, n_max_vocab=10)
        VOCAB, unkid = ks.upsert_word_to_vocab(VOCAB, "[UNK]")
        encoded = ks.encode_with_vocab(shingled, VOCAB, unkid)
        # Identify k's that are actually used
        klist = ks.shrink_k_backwards(encoded, unkid)
        # Step 2: Shingle sequences again
        shingled = [ks.shingling_list(s, klist=klist) for s in data]
        ...
    """
    k = len(encoded[0])
    klist = []
    for j in range(k):
        if not all([all([elem == unkid for elem in ex[j]]) for ex in encoded]):
            klist.append(j + 1)
    return klist


def encoded_with_vocab(x: Union[list, str],
                       VOCAB: List[str],
                       unkid: int) -> Union[list, int]:
    warnings.warn((
        "kshingle.encode_with_vocab will be removed in version '0.8.0'."
        " Please use kshingle.encode_with_vocab instead."
    ), DeprecationWarning, stacklevel=2)
    return encode_with_vocab(x, VOCAB, unkid)
