from . import yy


def test_simple():
    t = """
        {2+2}-{aa}-{aa+10}
    """

    s = yy.render(t, {'aa': 32})
    assert yy.nows(s) == '4-32-42'


def test_simple_format():
    t = """
        {2+2:04}-{aa!r}-{bb:.6f}
    """

    s = yy.render(t, {'aa': ['abc'], 'bb': 7.5})
    assert yy.nows(s) == "0004-['abc']-7.500000"


def test_expr_format():
    t = """
        @def foo a b c
            @return a + '-' + b + '-' + c
        @end
        {foo( 'X' 'Y' 'Z' ) + str(12 * 2) :*>10s}
    """

    s = yy.render(t)
    assert yy.nows(s) == "***X-Y-Z24"


def test_space_variants():
    t = """{ aa}|{aa}|{aa  }|{  }|{}|{  """

    s = yy.render(t, {'aa': 'ok'})
    assert s == '{ aa}|ok|ok|{  }|{}|{  '


def test_allow_space():
    t = """{ aa }"""

    s = yy.render(t, {'aa': 11}, echo_start_whitespace=False)
    assert s == t

    s = yy.render(t, {'aa': 11}, echo_start_whitespace=True)
    assert s == '11'
