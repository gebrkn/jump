from dataclasses import dataclass
from . import yy


def test_explicit_arg_get_dict():
    t = '>{ARGS["foo bar"].boo}<'
    d = {'foo bar': {'boo': 123}}
    s = yy.render(t, d)
    assert s == '>123<'


def test_explicit_arg_get_object():
    t = '>{ARGS.foo.boo}<'
    d = {'foo': {'boo': 123}}
    s = yy.render(t, d)
    assert s == '>123<'


def test__arg_get():
    t = '|{ARGS.get("yes")}|{ARGS.get("no")}|{ARGS.get("no2","dflt")}|'
    d = {'yes': 'YES'}
    s = yy.render(t, d)
    assert s == '|YES||dflt|'


def test_args_as_dict_in_code():
    t = """
        @code
            ARGS['one'] = 100
            ARGS['write'].append(5)
            return ARGS['foo'] + ARGS['one']
        @end
    """

    d = {'foo': 3, 'write': [1, 2]}
    s = yy.render(t, d)
    assert s == 103
    assert d['write'] == [1, 2, 5]


def test_args_as_object_in_code():
    t = """
        @code
            ARGS.one = 100
            ARGS.write.append(5)
            return ARGS.foo + ARGS.one
        @end
    """

    d = {'foo': 3, 'write': [1, 2]}
    s = yy.render(t, d)
    assert d['write'] == [1, 2, 5]


def test_args_writable():
    t = """
        >{two}<
        @code
            ARGS.one = 123
            ARGS.two = '!!!'
        @end
        >{one}<
        >{two}<
    """
    s = yy.render(t, {'two': '***'})
    assert yy.nows(s) == '>***<>123<>!!!<'


def test_object_args():
    t = '>{foo}{boo}{ARGS.zoo}<'

    class T:
        def __init__(self):
            self.foo = 1
            self.boo = 2
            self.zoo = 3

    d = T()

    s = yy.render(t, d)
    assert s == '>123<'


def test_object_args_dataclass():
    t = '>{foo}{boo}{ARGS.zoo}<'

    @dataclass
    class T:
        foo: int
        boo: int
        zoo: int

    d = T(foo=1, boo=2, zoo=3)

    s = yy.render(t, d)
    assert s == '>123<'


def test_object_args_dataclass_slots():
    t = '>{foo}{boo}{ARGS.zoo}<'

    @dataclass(slots=True)
    class T:
        foo: int
        boo: int
        zoo: int

    d = T(foo=1, boo=2, zoo=3)

    s = yy.render(t, d)
    assert s == '>123<'


def test_object_args_invalid():
    with yy.raises_runtime_error('arguments'):
        yy.render('hi', 13)
    with yy.raises_runtime_error('arguments'):
        yy.render('hi', [1, 2, 3])
