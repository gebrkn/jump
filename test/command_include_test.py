from . import yy


def test_include_paths(tmpdir):
    tmpdir.join('top1').write('TOP1')
    tmpdir.mkdir('sub1').join('a').write('SUB1_A')
    tmpdir.mkdir('sub2').join('b').write('SUB2_B')

    main = tmpdir.join('sub2', 'MAIN')
    main.write("""
            MAIN
            |
            @include ../sub1/a
            |
            @include ../top1
            |
            @include b
    """)

    s = yy.render_path(main.strpath)
    assert yy.nows(s) == 'MAIN|SUB1_A|TOP1|SUB2_B'


def test_include_deep(tmpdir):
    a = tmpdir.join('a')
    b = tmpdir.join('b')
    c = tmpdir.join('c')

    a.write('''
        A1<
        @include b
        >A2
    ''')
    b.write('''
        B1<
        @include c
        >B2
    ''')
    c.write('''
        C
    ''')

    s = yy.render_path(a.strpath)
    assert yy.nows(s) == 'A1<B1<C>B2>A2'


def test_include_inline(tmpdir):
    a = tmpdir.join('a')
    b = tmpdir.join('b')
    c = tmpdir.join('c')

    a.write('''A1<{@include b}>A2''')
    b.write('''B1<{@include c    }>B2''')
    c.write('''C''')

    s = yy.render_path(a.strpath)
    assert s == 'A1<B1<C>B2>A2'


def test_include_nested(tmpdir):
    a = tmpdir.join('a')
    b = tmpdir.join('b')

    a.write('''
        <
        @if 1
            @if 2
                @include b
            @end
            @if 2
                @include b
                @# comment
            @end
            @include b
            @if 2
                !!
            @end
        @end
        >
    ''')
    b.write('''
        B
    ''')

    s = yy.render_path(a.strpath)
    assert yy.nows(s) == '<BBB!!>'


def test_include_final(tmpdir):
    a = tmpdir.join('a')
    b = tmpdir.join('b')
    c = tmpdir.join('c')

    a.write('@include b')
    b.write('@include c')
    c.write('C')

    s = yy.render_path(a.strpath)
    assert yy.nows(s) == 'C'


def test_include_loader(tmpdir):
    t = """
            @include foo
            |
            @include bar
    """

    def loader(cur_path, path):
        return f'HI{path}', 'newpath'

    s = yy.render(t, loader=loader)
    assert yy.nows(s) == 'HIfoo|HIbar'


def test_error_location(tmpdir):
    inc1 = """\
        @# 1
        @# 2
        {err}
    """

    inc2 = """\
        @# 1
        {err}
        @# 3
    """

    tmpdir.join('inc1').write(inc1)
    tmpdir.join('inc2').write(inc2)

    tmpdir.join('main').write("""\
        @# 1
        @include inc1
        {err}
        @include inc2
        {err}
    """)

    s, err = yy.render_err(None, path=tmpdir.strpath + '/main')
    assert err == [
        'NameError in inc1 line 3',
        'NameError in main line 3',
        'NameError in inc2 line 2',
        'NameError in main line 5'
    ]
