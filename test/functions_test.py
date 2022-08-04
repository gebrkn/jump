from . import yy


def test_def():
    t = """
        @def ff (a, b)
            {a}/{b}
        @end

        |
        {ff(x, y)}
        |
        {ff(z, w)}
        |
    """

    s = yy.render(t, {
        'x': 'xx',
        'y': 'yy',
        'z': 'uu',
        'w': 'ww',
    })
    assert yy.nows(s) == '|xx/yy|uu/ww|'


def test_noargs():
    t = """
        @def ff
            bb
        @end
        |
        {ff()}
        |
    """

    s = yy.render(t)
    assert yy.nows(s) == '|bb|'


def test_relaxed_decl():
    t = """
        @def ff a b
            [ {a}-{b} ]
        @end
        
        {ff('aa','bb')}
    """
    s = yy.render(t)
    assert yy.nows(s) == '[aa-bb]'


def test_default_args():
    t = """
        @def ff a b='DEF'
            [ {a}-{b} ]
        @end
        
        {ff('aa')}
        {ff('aa', 'XYZ')}
        {ff('aa', b='UWV')}
    """
    s = yy.render(t)
    assert yy.nows(s) == '[aa-DEF][aa-XYZ][aa-UWV]'


def test_star_args():
    t = """
        @def ff a *b
            [ {a}-{b | join(',')} ]
        @end
        
        {ff('aa')}
        {ff('aa', 'X')}
        {ff('aa', 'X', 'Y')}
    """

    s = yy.render(t)
    assert yy.nows(s) == '[aa-][aa-X][aa-X,Y]'


def test_dstar_args():
    t = """
        @def ff a **b
            [ {a}-{b | json} ]
        @end
        
        {ff('aa', p=11, q=22)}
    """

    s = yy.render(t)
    assert yy.nows(s) == '[aa-{"p":11,"q":22}]'


def test_mixed_args():
    t = """
        @def ff a  b='ZZZ'  c=32+10  *args **kw
            [ {a}-{b}-{c}-{args}-{kw} ]
        @end
        
        {ff('aa' 11 22 33 44 foo=55 bar=66  )}
    """

    s = yy.render(t)
    assert yy.nows(s) == "[aa-11-22-(33,44)-{'foo':55,'bar':66}]"


def test_args_errors():
    t = """
        @def ff a ** b
        @end
    """

    with yy.raises_compiler_error():
        yy.render(t)


def test_return():
    t = """
        @def ff(a, b)
            ignored
            @return a + b
        @end

        |
        {ff(10, 200)}
        |
    """

    s = yy.render(t)
    assert yy.nows(s) == '|210|'


def test_top_level_return():
    t = """
        ignored
        @return 'abc'
        ignored
    """

    s = yy.render(t)
    assert yy.nows(s) == 'abc'


def test_return_none():
    t = """
        @def ff(a, b)
            begin
            @if a > b
                @return
            @end
            end
        @end

        |
        {ff(10, 200)}
        |
        {ff(1000, 200)}
    """

    s = yy.render(t)
    assert yy.nows(s) == '|beginend|'


def test_as_command():
    t = """
        @def ff(a, b)
            {a + b}
        @end

        |
        @ff 10, 200
        |
        @ff 10  200
        |
        @ff (
            10
            200)
        |
    """

    s = yy.render(t)
    assert yy.nows(s) == '|210|210|210|'


def test_as_command_var_args():
    t = """
        @def ff(a='A', b='B')
            {a + b}
        @end
        |
        @ff
        |
        @ff 'X'
        |
        @ff 'X' 'Y'
        |
        
    """

    s = yy.render(t)
    assert yy.nows(s) == '|AB|XB|XY|'


def test_as_command_with_keyword_args():
    t = """
        @def ff(a, b)
            {a + b}
        @end
        |
        @ff a=10, b=200
        |
        @ff a=10 b=200
        |
        @ff (
            a=10 
            b=200
        )
        |
    """

    s = yy.render(t)
    assert yy.nows(s) == '|210|210|210|'


def test_as_filter():
    t = """
        @def ff(a, b=200)
            {a + b}
        @end

        |
        {aa | ff}
        |
        {aa | ff(300)}
        |
    """
    d = {'aa': 5}
    s = yy.render(t, d)
    assert yy.nows(s) == '|205|305|'


def test_block():
    t = """
        @box foo(text, a, b)
            {a} {text} {b}
        @end

        @foo '>' '<'
            some
            text
        @end
    """
    s = yy.render(t)
    assert yy.nows(s) == '>sometext<'


def test_scope():
    t = '''
        @let c = 'C'
        
        @def use()
            [ {a},{b},{c} ]
        @end

        @def overwrite(b)
            @let c = 'newC'
            [ {a},{b},{c} ]
        @end
        
        [ {a},{b},{c}] 
        {use()}
        {overwrite('newB')}
    '''

    d = {'a': 'A', 'b': 'B'}
    s = yy.render(t, d)
    assert yy.nows(s) == '[A,B,C][A,B,C][A,newB,newC]'


def test_dynamic_scope():
    t = '''
        @let c = 0
        @let d = 0
        
        @def use()
            [ {a},{b},{c} ]
        @end

        @def overwrite(b)
            @let c = 'newC'
            [ {a},{b},{c} ]
        @end
        
        @let c = 'C'
        
        [ {a},{b},{c}] 
        {use()}
        {overwrite('newB')}
    '''

    d = {'a': 'A', 'b': 'B'}
    s = yy.render(t, d)
    assert yy.nows(s) == '[A,B,C][A,B,C][A,newB,newC]'


def test_mbox():
    t = '''
        @mbox mac(text, foo) = foo + (text|upper) + foo
        
        @mac '|'
            @if 1
                {esc}
            @bar
                {baz+}
        @end mac
    '''

    s = yy.render(t)
    assert yy.nows(s) == '|@IF1{ESC}@BAR{BAZ+}|'


def test_custom_command_overrides():
    t = '''
        @print 123
        
        @def print(x)
            hey({x+1})
        @end
        
        @print 345
    '''

    s = yy.render(t)
    assert yy.nows(s) == '123hey(346)'
