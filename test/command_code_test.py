from . import yy


def test_code():
    t = """
        |
        @code 
            print(2+2)
        @end
        |
        @code
            import sys
            print(sys.byteorder)
        @end
        |
    """

    import sys

    s = yy.render(t)
    assert yy.nows(s) == f'|4|{sys.byteorder}|'


def test_import():
    t = """
        @import sys
        @import os.path
        |
        {sys.byteorder}
        |
        {os.path.dirname('/foo/bar/baz')}
        |
    """

    import sys

    s = yy.render(t)
    assert yy.nows(s) == f'|{sys.byteorder}|/foo/bar|'


def test_code_syntax_error():
    t = """\
        @code
        a+b
        c
        d+
        @end
    """

    with yy.raises_compiler_error(':4'):
        yy.render(t)


def test_code_locals_are_isolated():
    t = """
        @code
        aa = 42
        def bb():
            return 43
        @end
    
        | {aa}
        | {bb}
        
    """

    s = yy.render(t, {'aa': '1', 'bb': 2})
    assert yy.nows(s) == f'|1|2'


def test_code_return_terminates_template():
    t = """
        ignored
        @code
            return 'abc'
        @end
        ignored
    """

    s = yy.render(t)
    assert yy.nows(s) == f'abc'


def test_code_runtime_error():
    t = """
        @#1
        @#2
        @code
            return 10 / 0
        @end
    """

    s, err = yy.render_err(t, path='PATH')
    assert err == ['ZeroDivisionError in PATH line 4']
