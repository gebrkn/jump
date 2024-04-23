from . import yy


def test_quote():
    t = """
        >
        @quote abc
            @if 123
            {foo}
            @end
            xyz
        @end abc
        <
    """
    s = yy.render(t)
    assert yy.nows(s) == '>@if123{foo}@endxyz<'


def test_quote_space():
    t = """
>
@quote a
ABC
@end a
|
@quote         b
   DEF
   @end   b
<"""
    s = yy.render(t)
    assert s == '\n>\nABC\n|\n   DEF\n<'


def test_quote_inline_space():
    t = """{@quote      a       }ABC{@end a}|{@quote b}DEF{@end         b   }"""
    s = yy.render(t)
    assert s == 'ABC|DEF'


def test_quote_with_custom_syntax():
    t = """
        @option inline_open_symbol = '[[[+++'
        @option inline_close_symbol = ']]]'
        @option command_symbol = '+++'
        
        +++quote a
            ABC
        +++end a
        |
        [[[+++quote      a]]]DEF[[[+++end a]]]
    """
    s = yy.render(t)
    assert yy.nows(s) == 'ABC|DEF'


def test_quote_nested():
    t = """
        >
        @quote abc
            @quote 123
                {foo}
            @end
            xyz
        @end abc
        <
    """
    s = yy.render(t)
    assert yy.nows(s) == '>@quote123{foo}@endxyz<'


def test_quote_inline():
    t = """
        >
        {@quote abc}
            @if 123
            {foo}
            @end{@end abc}
        <
    """
    s = yy.render(t)
    assert yy.nows(s) == '>@if123{foo}@end<'


def test_quote_inline_nested():
    t = """
        >
        {@quote abc}{@quote 123}
                {foo}{@end}{bar}{@end
                bbb}xyz{@end
                abc}
        <
    """
    s = yy.render(t)
    assert yy.nows(s) == '>{@quote123}{foo}{@end}{bar}{@endbbb}xyz<'


def test_quote_inline_no_label():
    t = """
        >
        @quote
            {foo}
        @end
        {@quote}{@bar}{@end}
        <
    """
    s = yy.render(t)
    assert yy.nows(s) == '>{foo}{@bar}<'


def test_skip():
    t = """
        >
        @skip abc
            @if 123
            {foo}
            @end
            xyz
        @end abc
        <
    """
    s = yy.render(t)
    assert yy.nows(s) == '><'

def test_comment():
    t = """
        >
        @comment abc
            @if 123
            {foo}
            @end
            xyz
        @end abc
        <
    """
    s = yy.render(t)
    assert yy.nows(s) == '><'


def test_skip_no_label():
    t = """
        >
        @skip
            {foo}
        @end
        <
    """
    s = yy.render(t)
    assert yy.nows(s) == '><'
