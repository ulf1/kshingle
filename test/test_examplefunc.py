from template_pypi.example import examplefunc


def test1():
    x = examplefunc(2.0)
    assert x == 4.0
