import re
import sys
import os
import time
import pytest

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + '/..')

import jump

lasterr = None


def lpr(s):
    for n, l in enumerate(s.split('\n'), 1):
        print(f'{n:6d}: {l}')


def translate(text, **opts):
    print('-' * 40)
    lpr(jump.translate(text, **opts))
    print('-' * 40)


def render(src, args=None, **opts):
    return jump.render(src, args, **opts)


def render_err(src, args=None, **opts):
    errors = []

    def err(exc, path, line, env):
        path = os.path.basename(path)
        errors.append(f'{type(exc).__name__} in {path} line {line}')

    res = jump.render(src, args, error=err, **opts)
    return res, errors


def render_path(path, args=None, **opts):
    global lasterr
    lasterr = None
    return jump.render_path(path, args, **opts)


def nows(s):
    return re.sub(r'\s+', '', s.strip())


def raises_template_error(exc):
    return pytest.raises(exc)


def raises_compiler_error(match=None):
    return pytest.raises(jump.CompileError, match=match)
