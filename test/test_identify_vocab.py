import kshingle as ks


def test1():
    # check length
    data = ['abc d abc de abc def', 'abc defg abc def gh abc def ghi']
    shingled = [ks.shingleseqs_k(s, k=9) for s in data]
    for n in range(1, 15):
        VOCAB = ks.identify_vocab(shingled, n_max_vocab=n)
        assert len(VOCAB) == n


def test2():
    data = ['a', 'ab']
    shingled = [ks.shingleseqs_k(s, k=2) for s in data]
    VOCAB = ks.identify_vocab(
        shingled, sortmode='prefer-shorter', n_min_count=1, n_max_vocab=None)
    assert VOCAB == ['a', 'b', 'ab']


def test3():
    data = ['a', 'ab']
    shingled = [ks.shingleseqs_k(s, k=2) for s in data]
    VOCAB = ks.identify_vocab(
        shingled, sortmode='times-length', n_min_count=1, n_max_vocab=None)
    assert VOCAB == ['a', 'ab', 'b']


def test4():
    data = ['a', 'ab']
    shingled = [ks.shingleseqs_k(s, k=2) for s in data]
    VOCAB = ks.identify_vocab(
        shingled, sortmode='sqrt-x-length', n_min_count=1, n_max_vocab=None)
    assert VOCAB == ['ab', 'a', 'b']


def test5():
    data = ['a', 'ab']
    shingled = [ks.shingleseqs_k(s, k=2) for s in data]
    VOCAB = ks.identify_vocab(
        shingled, sortmode='log-x-length', n_min_count=1, n_max_vocab=None)
    assert VOCAB == ['ab', 'a', 'b']
