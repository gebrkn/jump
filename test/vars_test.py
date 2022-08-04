from . import yy


def test_simple_var():
    t = '>{aa}<'
    d = {'aa': 123}
    s = yy.render(t, d)
    assert s == '>123<'


def test_nested_prop():
    t = '>{aa["bb"][0]["cc"]}<'
    d = {'aa': {'bb': [{'cc': 123}]}}
    s = yy.render(t, d)
    assert s == '>123<'


def test_nested_prop_dot_notation():
    t = '>{aa.bb[0].cc}<'
    d = {'aa': {'bb': [{'cc': 123}]}}
    s = yy.render(t, d)
    assert s == '>123<'


def test_nested_object():
    class C:
        xx = {'yy': 'zz'}

    t = '>{aa.bb.xx.yy}<'
    d = {'aa': {'bb': C()}}
    s = yy.render(t, d)
    assert s == '>zz<'


def test_methods():
    t = '''
        @for v in aa.values()
            [ {v} ]
        @end
    '''
    d = {'aa': {'a': 1, 'b': 2, 'c': 3}}
    s = yy.render(t, d)
    assert yy.nows(s) == '[1][2][3]'


def test_operators():
    t = '''
        [ {aa.x + bb.y * 4} ]
        [ {cc.z in [1,2,3]} ]
        [ {cc.z not in [4,5,6]} ]
        [ {3 < dd.w < 5} ]
        
    '''
    d = {'aa': {'x': 2}, 'bb': {'y': 10}, 'cc': {'z': 1}, 'dd': {'w': 4}}
    s = yy.render(t, d)
    assert yy.nows(s) == '[42][True][True][True]'


def test_if():
    t = '''
        [ {'yes' if aa else 'no'} ]
        [ {'yes' if bb else 'no'} ]
        
    '''
    d = {'aa': True, 'bb': False}
    s = yy.render(t, d)
    assert yy.nows(s) == '[yes][no]'


def test_local_var():
    t = '''
        [{aa.bb}]
        [{xx}]

        @let aa = {'bb': 'new'}
        @let xx = 'new2'

        [{aa.bb}]
        [{xx}]
    '''

    d = {'aa': {'bb': 'old'}, 'xx': 'old2'}
    s = yy.render(t, d)
    assert yy.nows(s) == '[old][old2][new][new2]'


def test_builtin_name():
    t = '>{len}{abs.__name__}{len("hello")}<'
    d = {}
    s = yy.render(t, d)
    assert s == '><built-in function len>abs5<'


def test_explicit_arg_dict():
    t = '>{ARGS["foo bar"].boo}<'
    d = {'foo bar': {'boo': 123}}
    s = yy.render(t, d)
    assert s == '>123<'
