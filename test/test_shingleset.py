import kshingle as ks


def test1():
    shingles = ks.shingleset_k("abc", k=3)
    assert shingles == set(["a", "b", "c", "ab", "bc", "abc"])


def test2():
    s1 = ks.shingleset_k("abc", k=3)
    s2 = ks.shingleset_range("abc", 1, 3)
    s3 = ks.shingleset_list("abc", [1, 2, 3])
    assert s1 == set(["a", "b", "c", "ab", "bc", "abc"])
    assert s2 == s1
    assert s3 == s2


def test3():
    s1 = ks.shingleset_list("abcde", [2, 4])
    assert s1 == set(["ab", "bc", "cd", "de", "abcd", "bcde"])


def test4():
    s1 = ks.shingleset_range("abcde", 3, 5)
    assert s1 == set(["abc", "bcd", "cde", "abcd", "bcde", "abcde"])
