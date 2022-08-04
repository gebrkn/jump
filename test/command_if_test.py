"""@if"""

from . import yy


def test_if():
    t = """
        @if aa > 1
            yes
        @end
    """
    s = yy.render(t, {'aa': 0})
    assert yy.nows(s) == ''
    s = yy.render(t, {'aa': 2})
    assert yy.nows(s) == 'yes'


def test_if_else():
    t = """
        @if aa > 1
            yes
        @else
            no
        @end
    """
    s = yy.render(t, {'aa': 2})
    assert yy.nows(s) == 'yes'
    s = yy.render(t, {'aa': 0})
    assert yy.nows(s) == 'no'


def test_if_elif():
    t = """
        @if aa > 10
            >10
        @elif aa > 5
            >5
        @else
            <=5
        @end
    """
    s = yy.render(t, {'aa': 20})
    assert yy.nows(s) == '>10'
    s = yy.render(t, {'aa': 8})
    assert yy.nows(s) == '>5'
    s = yy.render(t, {'aa': 4})
    assert yy.nows(s) == '<=5'


def test_nested_if():
    t = """
        @if aa > 5
            >5
            @if aa > 10
                >10
                @if aa > 20
                    >20
                @end
            @else
                <10
            @end
        @elif aa > 2
            >2
        @else
            <=2
            @if aa > 1
                =2
            @else
                =1
            @end
        @end
    """
    s = yy.render(t, {'aa': 25})
    assert yy.nows(s) == '>5>10>20'

    s = yy.render(t, {'aa': 15})
    assert yy.nows(s) == '>5>10'

    s = yy.render(t, {'aa': 5})
    assert yy.nows(s) == '>2'

    s = yy.render(t, {'aa': 2})
    assert yy.nows(s) == '<=2=2'

    s = yy.render(t, {'aa': 1})
    assert yy.nows(s) == '<=2=1'


def test_if_and_for():
    t = """
        @for x in '12345678' index n
            @if n == 3
                -a-
            @end
            @if n == 7
                -b-
            @end
            {x}
        @end
    """
    s = yy.render(t)
    assert yy.nows(s) == '12-a-3456-b-78'


