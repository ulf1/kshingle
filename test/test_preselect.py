import kshingle as ks
import pytest


def test1():
    db = {"ab": 3, "ac": 4, "ad": 5}
    shingle = "a"
    memo = ks.expandshingle(
        shingle, db=db, memo={}, wildcard="?", threshold=1.0,
        min_count_split=1, max_wildcards=0)
    assert memo == {}


def test2():
    db = {"ab": 3, "ac": 4, "ad": 5}
    shingle = "a"
    memo = ks.expandshingle(
        shingle, db=db, memo={}, wildcard="?", threshold=1.0,
        min_count_split=1, max_wildcards=1)
    assert memo == {'a?': 3, 'ac': 4, 'ad': 5}


def test3():
    with pytest.raises(Exception):
        memo = ks.expandshingle("a", db={}, memo={}, min_count_split=0)


def test4():
    db = {"qar": 2, "qbr": 3, "qcr": 4, "qdr": 5, "qer": 6, "qfr": 7}
    shingle = "qar"
    memo = ks.expandshingle(
        shingle, db=db, memo={}, wildcard="?", threshold=.8,
        min_count_split=1, max_wildcards=1)
    assert memo == {'q?r': 9, 'qdr': 5, 'qer': 6, 'qfr': 7}


def test4b():
    db = {"qar": 2, "qbr": 3, "qcr": 4, "qdr": 5, "qer": 6, "qfr": 7}
    memo = ks.preselect(
        db, wildcard="?", threshold=.8, min_count_split=1, max_wildcards=1)
    assert memo == {'q?r': 9, 'qdr': 5, 'qer': 6, 'qfr': 7}


def test5():
    db = {"ab": 2, "ac": 3, "abq": 4, "abr": 5}
    shingle = "ab"
    memo = ks.expandshingle(
        shingle, db=db, memo={}, wildcard="?", threshold=1,
        min_count_split=1, max_wildcards=2)
    assert memo == {'a?r': 5, 'ab?': 4, 'abr': 5}


def test6():
    db = {"ab": 2, "abq": 4, "xabq": 2, "yabq": 3}
    shingle = "ab"
    memo = ks.expandshingle(
        shingle, db=db, memo={}, wildcard="?", threshold=1,
        min_count_split=1, max_wildcards=2)
    assert memo == {'ab?': 4, '?ab?': 2, 'y??q': 3,
                    'y?bq': 3, 'ya?q': 3, 'yabq': 3}


def test6b():
    db = {"ab": 2, "abq": 4, "xabq": 2, "yabq": 3}
    memo = ks.preselect(
        db, wildcard="?", threshold=.8, min_count_split=3, max_wildcards=3)
    assert memo == {'ab?': 4, 'a?q': 4, 'y??q': 3, 
                    'y?bq': 3, 'ya?q': 3, 'yabq': 3}
