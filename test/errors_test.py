from . import yy


def test_no_var():
    t = """
        | {aa}
        | {bb}
    """

    s, err = yy.render_err(t, {}, path='PATH')
    assert err == ['NameError in PATH line 2', 'NameError in PATH line 3']
    assert yy.nows(s) == '||'

    with yy.raises_template_error(NameError):
        yy.render(t, {})


def test_no_key():
    t = """
        foo
        >{aa.bb}<
    """

    d = {'aa': 123}

    s, err = yy.render_err(t, d, path='PATH')
    assert err == ['AttributeError in PATH line 3']
    assert yy.nows(s) == 'foo><'

    with yy.raises_template_error(AttributeError):
        yy.render(t, d)


def test_code():
    t = """
        foo
        >{1/0}<
        bar
    """

    d = {'aa': 1}

    s, err = yy.render_err(t, d, path='PATH')
    assert err == ['ZeroDivisionError in PATH line 3']
    assert yy.nows(s) == 'foo><bar'

    with yy.raises_template_error(ZeroDivisionError):
        yy.render(t, d)
