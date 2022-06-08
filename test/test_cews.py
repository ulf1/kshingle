import kshingle as ks
import pytest
import functools
import itertools
from collections import Counter
import re


def test1():
    db = {"ab": 3, "ac": 4, "ad": 5}
    shingle = "a"
    memo = ks.expandshingle(
        shingle, db=db, memo={}, wildcard="?", threshold=1.0,
        min_samples_split=1, max_wildcards=0)
    assert memo == {}


def test2():
    db = {"ab": 3, "ac": 4, "ad": 5}
    shingle = "a"
    memo = ks.expandshingle(
        shingle, db=db, memo={}, wildcard="?", threshold=1.0,
        min_samples_split=1, max_wildcards=1)
    assert memo == {'a?': 3, 'ac': 4, 'ad': 5}


def test3():
    with pytest.raises(Exception):
        ks.expandshingle("a", db={}, memo={}, min_samples_split=0)


def test4():
    db = {"qar": 2, "qbr": 3, "qcr": 4, "qdr": 5, "qer": 6, "qfr": 7}
    shingle = "qar"
    memo = ks.expandshingle(
        shingle, db=db, memo={}, wildcard="?", threshold=.8,
        min_samples_split=1, max_wildcards=1)
    assert memo == {'q?r': 9, 'qdr': 5, 'qer': 6, 'qfr': 7}


def test4b():
    db = {"qar": 2, "qbr": 3, "qcr": 4, "qdr": 5, "qer": 6, "qfr": 7}
    memo = ks.cews(
        db, wildcard="?", threshold=.8, min_samples_split=1, max_wildcards=1)
    assert memo == {'q?r': 9, 'qdr': 5, 'qer': 6, 'qfr': 7}


def test5():
    db = {"ab": 2, "ac": 3, "abq": 4, "abr": 5}
    shingle = "ab"
    memo = ks.expandshingle(
        shingle, db=db, memo={}, wildcard="?", threshold=1,
        min_samples_split=1, max_wildcards=2)
    assert memo == {'a?r': 5, 'ab?': 4, 'abr': 5}


def test6():
    db = {"ab": 2, "abq": 4, "xabq": 2, "yabq": 3}
    shingle = "ab"
    memo = ks.expandshingle(
        shingle, db=db, memo={}, wildcard="?", threshold=1,
        min_samples_split=1, max_wildcards=2)
    assert memo == {'ab?': 4, '?ab?': 2, 'y??q': 3,
                    'y?bq': 3, 'ya?q': 3, 'yabq': 3}


# def test6b():
#     db = {"ab": 2, "abq": 4, "xabq": 2, "yabq": 3}
#     memo = ks.cews(
#         db, wildcard="?", threshold=.8, min_samples_split=3, max_wildcards=3)
#     assert memo == {'ab?': 4, 'a?q': 4, 'y?bq': 3, 'y??q': 3, 'ya?q': 3}


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
    memo = ks.cews(db, threshold=0.8, min_samples_split=10, max_wildcards=2)
    # encode shingles with patterns
    PATTERNS = ks.shingles_to_patterns(memo)
    encoded = ks.encode_with_patterns(shingled, PATTERNS, len(PATTERNS))
    assert sum([len(pats) for pats in PATTERNS.values()]) == len(memo)
    assert len(encoded) == len(shingled)
    for i in range(len(encoded)):
        assert len(encoded[i]) == len(shingled[i])
        for j in range(len(encoded[i])):
            assert len(encoded[i][j]) == len(shingled[i][j])


def test8():
    memo = {"*a": 1, "a*b": 1, "a*": 1, "a": 1}
    PATTERNS = ks.shingles_to_patterns(memo, wildcard="*")
    assert [p.pattern for p in PATTERNS[1]] == ["^a$"]
    assert [p.pattern for p in PATTERNS[2]] == ["^\\w{1}a$", "^a\\w{1}$"]
    assert [p.pattern for p in PATTERNS[3]] == ["^a\\w{1}b$"]


# def test9():
#     # rare edge cases
#     k = 5
#     docs = [
#         "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam ",
#         "nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam ",
#         "erat, sed diam voluptua. At vero eos et accusam et justo duo ",
#         "dolores et ea rebum. Stet clita kasd gubergren, no sea takimata "]
#     # generate all shingles
#     shingled = [ks.shingleseqs_k(doc, k=k) for doc in docs]
#     assert len(shingled) == len(docs)
#     assert len(shingled[0]) == k
#     # run CEWS algorithm
#     db = functools.reduce(lambda x, y: x + Counter(itertools.chain(*y)),
#                           shingled, Counter([]))
#     memo = ks.cews(
#         db, max_wildcards=1, min_samples_leaf=0.0005,
#         threshold=0.9)
#     memo = ks.cews(
#         db, max_wildcards=1, vocab_size=500,
#         min_samples_leaf='auto', threshold=0.9)
#     memo = ks.cews(
#         db, max_wildcards=1, priority='rare',
#         min_samples_leaf=1, threshold=0.9)


def test10():
    k = 5
    corpus = [
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam ",
        "nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam ",
        "erat, sed diam voluptua. At vero eos et accusam et justo duo ",
        "dolores et ea rebum. Stet clita kasd gubergren, no sea takimata "]
    # generate all shingles
    shingled = [ks.shingleseqs_k(doc, k=k) for doc in corpus]
    assert len(shingled) == len(corpus)
    assert len(shingled[0]) == k
    # run CEWS algorithm
    db = functools.reduce(lambda x, y: x + Counter(itertools.chain(*y)),
                          shingled, Counter([]))
    memo = ks.cews(db, threshold=0.8, min_samples_split=10, max_wildcards=2)
    PATTERNS = ks.shingles_to_patterns(memo)
    unkid = sum([len(pats) for pats in PATTERNS.values()])
    # encode
    encoded, shingled = ks.encode_multi_match_corpus(
        corpus, k=k, PATTERNS=PATTERNS, num_matches=3, unkid=unkid, stack=True)
    assert encoded.shape[1] == 3 * k - 3


def test11():
    k = 5
    text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam "
    # generate all shingles
    shingled = ks.shingleseqs_k(text, k=k)
    # run CEWS algorithm
    db = functools.reduce(lambda x, y: x + Counter(itertools.chain(*y)),
                          shingled, Counter([]))
    memo = ks.cews(db, threshold=0.8, min_samples_split=10, max_wildcards=2)
    PATTERNS = ks.shingles_to_patterns(memo)
    unkid = sum([len(pats) for pats in PATTERNS.values()])
    # encode
    encoded, shingled = ks.encode_multi_match_corpus(
        [text], k=k, PATTERNS=PATTERNS, num_matches=3, unkid=unkid, stack=True)
    assert encoded.shape[1] == 3 * k - 3
    # encode
    encoded2 = ks.encode_multi_match_text(
        text, k=k, PATTERNS=PATTERNS, num_matches=3, unkid=unkid)
    assert encoded2.shape == encoded.shape
    assert (encoded2 == encoded).all()


def test12():
    k = 5
    corpus = [
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam ",
        "nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam ",
        "erat, sed diam voluptua. At vero eos et accusam et justo duo ",
        "dolores et ea rebum. Stet clita kasd gubergren, no sea takimata "]
    # generate all shingles
    shingled = [ks.shingleseqs_k(doc, k=k) for doc in corpus]
    assert len(shingled) == len(corpus)
    assert len(shingled[0]) == k
    # run CEWS algorithm
    db = functools.reduce(lambda x, y: x + Counter(itertools.chain(*y)),
                          shingled, Counter([]))
    memo = ks.cews(db, threshold=0.8, min_samples_split=10, max_wildcards=2)
    PATTERNS = ks.shingles_to_patterns(memo)
    unkid = sum([len(pats) for pats in PATTERNS.values()])
    PATTERNS[1].append(re.compile(r"^[UNK]$"))
    padid = sum([len(pats) for pats in PATTERNS.values()])
    PATTERNS[1].append(re.compile(r"^[PAD]$"))
    # encode
    encbatch = ks.encode_multi_match_batch(
        corpus, k=k, PATTERNS=PATTERNS, num_matches=3,
        unkid=unkid, seqlen=32, padid=padid)
    assert encbatch[0].shape[1] == 3 * k - 3
    assert encbatch[0].shape[0] == 32
