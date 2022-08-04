from . import yy


def test_filter_safe():
    t = '>{aa | safe}<'
    d = {'aa': 'bb'}
    s = yy.render(t, d)
    assert s == '>bb<'


def test_filter_as_int():
    t = '>{aa | as_int}<'
    d = {'aa': '0000099'}
    s = yy.render(t, d)
    assert s == '>99<'


def test_filter_as_float():
    t = '>{aa | as_float}<'
    d = {'aa': '0000099.770000'}
    s = yy.render(t, d)
    assert s == '>99.77<'


def test_filter_as_str():
    t = '>{aa | as_str}<'
    d = {'aa': 123}
    s = yy.render(t, d)
    assert s == '>123<'


def test_filter_html():
    t = '>{aa | html}<'
    d = {'aa': '<b>'}
    s = yy.render(t, d)
    assert s == '>&lt;b&gt;<'


def test_filter_nl2br():
    t = '>{aa | nl2br}<'
    d = {'aa': 'aa\nbb'}
    s = yy.render(t, d)
    assert s == '>aa<br/>bb<'


def test_filter_strip():
    t = '>{aa | strip}<'
    d = {'aa': '  123  '}
    s = yy.render(t, d)
    assert s == '>123<'


def test_filter_upper():
    t = '>{aa | upper}<'
    d = {'aa': 'abcDEF'}
    s = yy.render(t, d)
    assert s == '>ABCDEF<'


def test_filter_lower():
    t = '>{aa | lower}<'
    d = {'aa': 'abcDEF'}
    s = yy.render(t, d)
    assert s == '>abcdef<'


def test_filter_linkify():
    t = '>{aa | linkify}<'
    d = {'aa': 'abc https://www.com def https://www.com, xyz'}
    s = yy.render(t, d)
    assert s == '>abc <a href="https://www.com">https://www.com</a> def <a href="https://www.com">https://www.com</a>, xyz<'


def test_filter_unhtml():
    t = '>{aa | unhtml}<'
    d = {'aa': '<b> abc &lt;b&gt;'}
    s = yy.render(t, d)
    assert s == '><b> abc <b><'


def test_filter_format():
    t = '>{aa | format("03d")}<'
    d = {'aa': 7}
    s = yy.render(t, d)
    assert s == '>007<'


def test_filter_cut():
    t = '>{aa | cut(3)}<'
    d = {'aa': '0123456'}
    s = yy.render(t, d)
    assert s == '>012<'

    t = '>{aa | cut(3, "@")}<'
    d = {'aa': '0123456'}
    s = yy.render(t, d)
    assert s == '>012@<'

    t = '>{aa | cut(333)}<'
    d = {'aa': '0123456'}
    s = yy.render(t, d)
    assert s == '>0123456<'


def test_filter_shorten():
    t = '>{aa | shorten(5)}<'
    d = {'aa': '0123456'}
    s = yy.render(t, d)
    assert s == '>01256<'

    t = '>{aa | shorten(4)}<'
    d = {'aa': '0123456'}
    s = yy.render(t, d)
    assert s == '>0156<'

    t = '>{aa | shorten(5, "@")}<'
    d = {'aa': '0123456'}
    s = yy.render(t, d)
    assert s == '>012@56<'

    t = '>{aa | shorten(333)}<'
    d = {'aa': '0123456'}
    s = yy.render(t, d)
    assert s == '>0123456<'


def test_filter_slice():
    t = '>{aa | slice(1, 4)}<'
    d = {'aa': '0123456'}
    s = yy.render(t, d)
    assert s == '>123<'


def test_filter_json():
    class C:
        def __init__(self):
            self.aa = 'füßchen'
            self.bb = 'yy'

    t = '>{aa | json}<'
    d = {'aa': {'cc': C()}}
    s = yy.render(t, d)
    assert s == r'>{"cc": {"aa": "f\u00fc\u00dfchen", "bb": "yy"}}<'


def test_combined_filters():
    t = '>{aa | upper | html | repr}<'
    d = {'aa': '<b>A\n'}
    s = yy.render(t, d)
    assert s == ">'&lt;B&gt;A\\n'<"


def test_default_filter():
    t = '>{aa}<'
    d = {'aa': '<b>A'}
    s = yy.render(t, d, filter='html')
    assert s == '>&lt;b&gt;A<'


def test_inline_default_filter():
    t = '''
        @option filter = 'html'
        >{aa}<
    '''
    d = {'aa': '<b>A'}
    s = yy.render(t, d)
    assert yy.nows(s) == '>&lt;b&gt;A<'


def test_filter_expression():
    t = '''
        @def f(x, y)
            >{x}<>{y}<
        @end
        
        @f 'abc' | upper  'def' | cut(2) 
        
    '''

    s = yy.render(t, {})
    assert yy.nows(s) == '>ABC<>de<'
