import kshingle as ks
import pytest
import functools
import itertools
from collections import Counter


def test4b():
    db = {"qar": 2, "qbr": 3, "qcr": 4, "qdr": 5, "qer": 6, "qfr": 7}
    memo = ks.cews_cpu(
        db, wildcard="?", threshold=.8, min_count_split=1, max_wildcards=1)
    assert memo == {'q?r': 9, 'qdr': 5, 'qer': 6, 'qfr': 7}


def test7():
    k = 5
    docs = [
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam ",
        "nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam ",
        "erat, sed diam voluptua. At vero eos et accusam et justo duo ",
        "dolores et ea rebum. Stet clita kasd gubergren, no sea takimata "]
    # generate all shingles
    shingled = [ks.shingleseqs_k(doc, k=k) for doc in docs]
    assert len(shingled) == len(docs)
    assert len(shingled[0]) == k
    # run CEWS algorithm
    db = functools.reduce(lambda x, y: x + Counter(itertools.chain(*y)),
                          shingled, Counter([]))
    memo = ks.cews_cpu(db, threshold=0.8, min_count_split=10, max_wildcards=2)
    # encode shingles with patterns
    PATTERNS = ks.shingles_to_patterns(memo)
    encoded = ks.encode_with_patterns(shingled, PATTERNS, len(PATTERNS))
    assert len(PATTERNS) == len(memo)
    assert len(encoded) == len(shingled)
    for i in range(len(encoded)):
        assert len(encoded[i]) == len(shingled[i])
        for j in range(len(encoded[i])):
            assert len(encoded[i][j]) == len(shingled[i][j])


def test8():
    memo = {"*a": 1, "a*b": 1, "a*": 1, "a": 1}
    PATTERNS = ks.shingles_to_patterns(memo, wildcard="*")
    assert [p.pattern[1:-1] for p in PATTERNS] == [
        "a", "a\\w{1}b", "\\w{1}a", "a\\w{1}"]
