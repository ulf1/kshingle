import kshingle as ks


def test1():
    A = {'a', 'b', 'ab'}
    B = {'a'}
    score = ks.jaccard(A, B)
    assert score == 1 / 3


def test2():
    k = 1
    A = ks.shingleset_k("hamsterkäufe", k)
    B = ks.shingleset_k("hamsterkauf", k)
    score = ks.jaccard(A, B)
    assert 0.909 < score < 0.910


def test3():
    k = 8
    A = ks.shingleset_k("hamsterkäufe", k)
    B = ks.shingleset_k("hamsterkauf", k)
    score = ks.jaccard(A, B)
    assert 0.448 < score < 0.449


def test4():
    k = 8
    A = ks.shingleset_k("hamsterkäufe", k)
    A = A.union(ks.wildcard_shinglesets(A, n_max_wildcards=1))
    B = ks.shingleset_k("hamsterkauf", k)
    B = B.union(ks.wildcard_shinglesets(B, n_max_wildcards=1))
    score = ks.jaccard(A, B)
    assert 0.412 < score < 0.413


def test5():
    s1 = "hamsterkäufe"
    s2 = "hamsterkauf"
    k = 8
    score = ks.jaccard_strings(s1, s2, k)
    assert 0.448 < score < 0.449


def test6():
    s1 = "hamsterkäufe"
    s2 = "hamsterkauf"
    k = 8
    n_max_wildcards = 1
    score = ks.jaccard_strings(s1, s2, k, n_max_wildcards)
    assert 0.412 < score < 0.413
