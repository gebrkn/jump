"""@for"""

from . import yy


#
def test_value():
    t = """
        @for e in it
            {e}!
        @end
    """
    d = {'it': ['aaa', 'bbb', 'ccc']}
    s = yy.render(t, d)
    assert yy.nows(s) == 'aaa!bbb!ccc!'


def test_key_value():
    t = """
        @for key val in it
            {key}={val}!
        @end
    """
    d = {'it': {'aaa': 0, 'bbb': 1, 'ccc': 2}}
    s = yy.render(t, d)
    assert yy.nows(s) == 'aaa=0!bbb=1!ccc=2!'


def test_index():
    t = """
        @for e in it index k
            {e}={k}!
        @end
    """
    d = {'it': ['aaa', 'bbb', 'ccc']}
    s = yy.render(t, d)
    assert yy.nows(s) == 'aaa=1!bbb=2!ccc=3!'


def test_length():
    t = """
        @for e in it length total
           {total}-{e}!
        @end
    """
    d = {'it': ['aaa', 'bbb', 'ccc']}
    s = yy.render(t, d)
    assert yy.nows(s) == '3-aaa!3-bbb!3-ccc!'


def test_index_length():
    t = """
        @for e in it index k length total
            {k}-{total}-{e}!
        @end
    """
    d = {'it': ['aaa', 'bbb', 'ccc']}
    s = yy.render(t, d)
    assert yy.nows(s) == '1-3-aaa!2-3-bbb!3-3-ccc!'


def test_empty():
    t = """
        >
        @for e in it
            {e}
        @end
        <
    """
    d = {'it': []}
    s = yy.render(t, d)
    assert yy.nows(s) == '><'


def test_empty_else():
    t = """
        >
        @for e in it
            {e}
        @else
            EMPTY!
        @end
        <
    """
    d = {'it': []}
    s = yy.render(t, d)
    assert yy.nows(s) == '>EMPTY!<'


def test_break_continue():
    t = """
        @for x in '12345678' index n
            @if n == 3
                @continue
            @end
            @if n == 7
                @break
            @end
            {x}
        @end
    """

    s = yy.render(t)
    assert yy.nows(s) == '12456'


def test_unexpected_break():
    t = """
        >
        @break
        <
    """

    with yy.raises_compiler_error():
        yy.render(t)

    t = """
        >
        @for x in y
            @def z
                @break
            @end
        @end
        <
    """

    with yy.raises_compiler_error():
        yy.render(t)


def test_unexpected_continue():
    t = """
        >
        @continue
        <
    """

    with yy.raises_compiler_error():
        yy.render(t)

    t = """
        >
        @for x in y
            @def z
                @continue
            @end
        @end
        <
    """

    with yy.raises_compiler_error():
        yy.render(t)


def test_error_non_iter():
    t = """
        >
        @for e in 123 length a
            {e}
        @end
        <
    """

    d = {}
    s, err = yy.render_err(t, d)
    assert yy.nows(s) == '><'


def test_error_undef():
    t = """
        >
        @for e in UNDEF
            {e}
        @end
        <
    """
    d = {}
    s, err = yy.render_err(t, d)
    assert yy.nows(s) == '><'
