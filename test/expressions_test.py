from . import yy


def _tpl_eval(expr):
    tpl = f'''
        @let x = {expr}
        @code
            ARGS['ret'] = x
        @end
    '''
    args = {}
    yy.render(tpl, args)
    return args['ret']


def test_literals():
    exprs = [
        '123',
        '123.456'
        '123e-4',
        '0x123',
        '0o123',
        '0b11011',
    ]

    for e in exprs:
        assert _tpl_eval(e) == eval(e)

    assert _tpl_eval('123_45_678') == 12345678

    exprs = [
        r'"hello"',
        r'"hello\0"',
        r'"\n\r\thello\0"',
        r'"hello\x21"',
        r'"hello\x21"',
        r'"hello\u1234"',
        r'"hello\U00101234"',
        r'"hello\U00101234"',
    ]

    for e in exprs:
        assert _tpl_eval(e) == eval(e)

    assert _tpl_eval(r'"foo\u{1234}bar"') == 'foo\U00001234bar'

    exprs = [
        r'[1, 2, "hello"]',
        r'[1, 2, "hello",]',
        r'[]',
        r'[      ]',
        r'{"foo":"bar", 123: "baz"}',
        r'{"foo":"bar", 123: "baz",}',
        r'{   }',
    ]

    for e in exprs:
        assert _tpl_eval(e) == eval(e)

    assert _tpl_eval('[11 22 33]'), [11, 22, 33]
    assert _tpl_eval('{"a": 1 "b":  2}'), {'a': '1', 'b': '2'}


def test_primary():
    exprs = [
        '123 * (456 + 678)',
        'compile.__name__',
        'compile.__name__.upper()[0]',
        'compile.__name__[:2]',
        'compile.__name__[1:2:3]',
        '[1,2,3,4,5,6,7,8][:]',
        '[1,2,3,4,5,6,7,8][::]',
        '[1,2,3,4,5,6,7,8][2:]',
        '[1,2,3,4,5,6,7,8][:2]',
        '[1,2,3,4,5,6,7,8][:2:]',
        '[1,2,3,4,5,6,7,8][:2:3]',
    ]

    for e in exprs:
        assert _tpl_eval(e) == eval(e)

    with yy.raises_compiler_error():
        _tpl_eval('[1][::::]')

    with yy.raises_compiler_error():
        _tpl_eval('[1][1:2:3:4:]')


def test_expressions():
    exprs = [
        '2 if 1 else 3',
        '2 + 3 * 4 if not 2 + 3 * 4 else 4 + 5 * 6',
        '1 or 2',
        '1 and 2',
        'not 3',
        '1 < 5',
        '1 < 5 < 6',
        '1 + 5 * 6 - 7 / 8',
        '2 ** 3 ** 4',
        '1 + 2 ** 3 * 4 ** 5',
        '1 + 2 ** 3 if 5 < 6 else 4 + 5 ** 6',
        '1 + 2 ** (3 if 5 < 6 else 4) + 5 ** 6',
    ]

    for e in exprs:
        assert _tpl_eval(e) == eval(e)

    with yy.raises_compiler_error():
        _tpl_eval('max (0, 1)')


def test_funcalls():
    assert _tpl_eval('int("12", 8)') == int("12", 8)
    assert _tpl_eval('int("1" + "2", 10 - 2)') == int("12", 8)


def test_funcalls_no_comma():
    assert _tpl_eval('int("12"  8)') == int("12", 8)
    assert _tpl_eval('int("1" + "2" 10-2)') == int("12", 8)


def test_spacing():
    assert _tpl_eval('[1 + 2]') == [3]
    assert _tpl_eval('[1 +2]') == [1, 2]

    with yy.raises_compiler_error():
        yy.render('{[1+ 2]}')

    assert _tpl_eval('max(0, 1 + 2+3)') == 6
    assert _tpl_eval('max(0, 1 +2 +3)') == 3

    with yy.raises_compiler_error():
        _tpl_eval('max (0, 1)')
