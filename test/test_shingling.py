import kshingle as ks


def test1():
    shingles = ks.shingling_k("", 1)
    assert shingles == [[]]

    shingles = ks.shingling_k(" ", 1)
    assert shingles == [[" "]]

    shingles = ks.shingling_k(" ", 2)
    assert shingles == [[" "], []]


def test2():
    shingles = ks.shingling_k(" ", 0)
    assert shingles == []

    shingles = ks.shingling_k(" ", -1)
    assert shingles == []


def test3():
    shingles = ks.shingling_k("12345", 0)
    assert shingles == []

    shingles = ks.shingling_k("12345", 1)
    assert shingles == [['1', '2', '3', '4', '5']]

    shingles = ks.shingling_k("12345", 2)
    assert shingles == [
        ['1', '2', '3', '4', '5'],
        ['12', '23', '34', '45']]

    shingles = ks.shingling_k("12345", 3)
    assert shingles == [
        ['1', '2', '3', '4', '5'],
        ['12', '23', '34', '45'],
        ['123', '234', '345']]

    shingles = ks.shingling_k("12345", 4)
    assert shingles == [
        ['1', '2', '3', '4', '5'],
        ['12', '23', '34', '45'],
        ['123', '234', '345'],
        ['1234', '2345']]

    shingles = ks.shingling_k("12345", 5)
    assert shingles == [
        ['1', '2', '3', '4', '5'],
        ['12', '23', '34', '45'],
        ['123', '234', '345'],
        ['1234', '2345'],
        ['12345']]

    shingles = ks.shingling_k("12345", 6)
    assert shingles == [
        ['1', '2', '3', '4', '5'],
        ['12', '23', '34', '45'],
        ['123', '234', '345'],
        ['1234', '2345'],
        ['12345'], []]


def test11():
    shingles = ks.shingling_range("", 0, 1)
    assert shingles == [[]]

    shingles = ks.shingling_range(" ", 0, 1)
    assert shingles == [[" "]]

    shingles = ks.shingling_range(" ", 0, 2)
    assert shingles == [[" "], []]

    shingles = ks.shingling_range("", 1, 1)
    assert shingles == [[]]

    shingles = ks.shingling_range(" ", 1, 1)
    assert shingles == [[" "]]

    shingles = ks.shingling_range(" ", 1, 2)
    assert shingles == [[" "], []]


def test12():
    shingles = ks.shingling_range("", -10, -10)
    assert shingles == []

    shingles = ks.shingling_range("", 0, 0)
    assert shingles == []

    shingles = ks.shingling_range("", 4, 1)
    assert shingles == []


def test31():
    shingles = ks.shingling_list("", [1])
    assert shingles == [[]]

    shingles = ks.shingling_list(" ", [1])
    assert shingles == [[" "]]

    shingles = ks.shingling_list(" ", [1, 2])
    assert shingles == [[" "], []]


def test32():
    shingles = ks.shingling_list(" ", [0])
    assert shingles == []

    shingles = ks.shingling_list(" ", [-1])
    assert shingles == []


def test33():
    shingles = ks.shingling_list("12345", [5, 6])
    assert shingles == [['12345'], []]

    shingles = ks.shingling_list("12345", [0, 3, 6])
    assert shingles == [['123', '234', '345'], []]  # this is a problem!
