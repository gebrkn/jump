from . import yy


def test_let_expr():
    t = """
        @let foo = 123
        {foo}
    """
    s = yy.render(t)
    assert yy.nows(s) == '123'


def test_let_expr_multi():
    t = """
        @let aa bb,   cc   = '123'
        {aa}-{bb}-{cc}
    """
    s = yy.render(t)
    assert yy.nows(s) == '1-2-3'


def test_let_block():
    t = """
        @let foo
            abc
            def
        @end
        {foo}
    """
    s = yy.render(t)
    assert yy.nows(s) == 'abcdef'


def test_do():
    t = """
        @let a = [1 2 3]
        @let b = [4 5 6]
        @do a.insert(1 11), b.insert(2 22)
        |
        {a|join(',')} 
        |
        {b|join(',')}
        | 
    """
    s = yy.render(t)
    assert yy.nows(s) == '|1,11,2,3|4,5,22,6|'
