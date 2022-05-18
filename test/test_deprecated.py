import kshingle as ks
import functools
import itertools
from collections import Counter


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
    # encode
    encoded, shingled = ks.encode_multi_match_corpus(
        corpus, k=k, PATTERNS=PATTERNS, num_matches=3, stack=True)
    assert encoded.shape[1] == 3 * k - 3
