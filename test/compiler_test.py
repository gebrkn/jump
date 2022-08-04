from . import yy


def test_syntax():
    with yy.raises_compiler_error():
        yy.render("{1+}")

    with yy.raises_compiler_error():
        yy.render("@blah")

    with yy.raises_compiler_error():
        yy.render("@let $$$")

    with yy.raises_compiler_error():
        yy.render("@if a")

    with yy.raises_compiler_error():
        yy.render("@end")

    with yy.raises_compiler_error():
        yy.render("@else")

    with yy.raises_compiler_error():
        yy.render("""
            @if 1
                1
            @else
                2
            @else
                3
            @end
        """)

    with yy.raises_compiler_error():
        yy.render("@def ...")

    with yy.raises_compiler_error():
        yy.render("@include bleh")

    with yy.raises_compiler_error():
        yy.render("{a & b}")



def test_line_numbers():
    t = """\
        @# 1
        @# 2
        @for x
    """

    with yy.raises_compiler_error(':3'):
        yy.render(t)



def test_command_labels():
    t = """
        @if 1
            @for a in [1,2,3]
                {a}
            @end for
        @end if
    """
    s = yy.render(t)
    assert yy.nows(s) == '123'


def test_custom_command_labels():
    t = """
        @box foo a
            |{a}|
        @end
        @foo
            hi
        @end foo
    """
    s = yy.render(t)
    assert yy.nows(s) == '|hi|'


def test_command_wrong_labels():
    t = """\
        @if 1
            @for a in [1,2,3]
                {a}
            @end if
        @end
    """
    with yy.raises_compiler_error(':4'):
        yy.render(t)


def test_inline_command():
    t = """
        {@if 1}1{@end}
        {@if a    }2{@else}3{@end        }
    """
    s = yy.render(t, {'a': True})
    assert yy.nows(s) == '12'
    s = yy.render(t, {'a': False})
    assert yy.nows(s) == '13'


def test_inline_custom_command():
    t = """
        @def foo a='A' b='B' c='C'
            @return a + '-' + b + '-' + c
        @end
        | {@foo}
        | {@foo 'X'}
        | {@foo 'X' 'Y'}
        | {@foo 'X' 'Y' 'Z'}
        | {@foo c='Z'}
        |
    """

    s = yy.render(t)
    assert yy.nows(s) == '|A-B-C|X-B-C|X-Y-C|X-Y-Z|A-B-Z|'


def test_inline_not_a_command():
    t = """
        {@ if}
        { @if}
        { @ if}
    """
    s = yy.render(t)
    assert yy.nows(s) == '{@if}{@if}{@if}'


def test_custom_symbols():
    t = """
        %if aa
            // comment
            <% aa+10 %>
        %end
    """
    syntax = {
        'comment_symbol': '//',
        'command_symbol': '%',
        'echo_open_symbol': '<%',
        'echo_close_symbol': '%>',
        'echo_start_whitespace': True,
    }

    s = yy.render(t, {'aa': 32}, **syntax)
    assert yy.nows(s) == '42'


def test_escapes():
    t = r"""
        {a}
        {{a}
        {{b}}
        @if 1
            {b}
        @end
        @@if 1
            {b}
        @@end
        @let x = '\{abc\}'
        {x}
    """
    s = yy.render(t, {'a': 'A', 'b': 'B'})
    assert yy.nows(s) == 'A{a}{b}B@if1B@end{abc}'


def test_whitespace():
    t = """\
abc
@if 1
    def
        ghi
        @ no command
        {aa} var
        { aa } no var
@end"""
    s = yy.render(t, {'aa': 'AA'}, strip=True)
    assert s == """\
abc
def
ghi
@ no command
AA var
{ aa } no var
"""

    s = yy.render(t, {'aa': 'AA'}, strip=False)
    assert s == """\
abc
    def
        ghi
        @ no command
        AA var
        { aa } no var
"""


def test_whitespace_quote():
    t = """\
        abc
            @quote
                def
                    ghi
            @end
        xyz
    """
    s = yy.render(t, {'aa': 'AA'}, strip=True)
    assert s == """\
abc
                def
                    ghi
xyz
"""
