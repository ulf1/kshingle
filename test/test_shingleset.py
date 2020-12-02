import kshingle as ks


def test1():
    shingles = ks.shingleset_k("abc", k=3)
    assert shingles == set(["a", "b", "c", "ab", "bc", "abc"])
