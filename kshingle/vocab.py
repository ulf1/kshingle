from typing import List, Optional
import functools
import itertools
import collections
import math


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
