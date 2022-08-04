from . import yy


def test_with_empty():
    t = """
        >
        @with aa
            yes
        @end
        <
    """

    s = yy.render(t)
    assert yy.nows(s) == '><'

    s = yy.render(t, {'aa': ''})
    assert yy.nows(s) == '><'

    s = yy.render(t, {'aa': {}})
    assert yy.nows(s) == '><'


def test_with_not_empty():
    t = """
        >
        @with aa
            yes
        @end
        <
    """

    s = yy.render(t, {'aa': 1})
    assert yy.nows(s) == '>yes<'

    s = yy.render(t, {'aa': 0})
    assert yy.nows(s) == '>yes<'


def test_with_else():
    t = """
        >
        @with aa
            yes
        @else
            no
        @end
        <
    """

    s = yy.render(t, {'aa': 1})
    assert yy.nows(s) == '>yes<'

    s = yy.render(t, {'aa': ''})
    assert yy.nows(s) == '>no<'

    s = yy.render(t)
    assert yy.nows(s) == '>no<'


def test_with_ref():
    t = """
        >
        @with aa as x
            {x.bb}
        @end
        <
    """
    s = yy.render(t, {'aa': {'bb': 456}})
    assert yy.nows(s) == '>456<'


def test_with_nested():
    t = """
        >
        @with aa as x
            ({aa.bb.cc})
            @with x.bb as y
                ({y.cc})
                @with y.cc as z
                    ({z})
                @end
            @end
        @end
        <
    """
    s = yy.render(t, {'aa': {'bb': {'cc': 11}}})
    assert yy.nows(s) == '>(11)(11)(11)<'


def test_without():
    t = """
        >
        @without aa
            no<aa>
        @else
            have<aa>
        @end
        @without bb
            no<bb>
        @else
            have<bb>
        @end
        <
    """
    s = yy.render(t, {'aa': 1})
    assert yy.nows(s) == '>have<aa>no<bb><'
