"""Smoke test."""

from . import yy


def test_empty():
    t = ""
    s = yy.render(t)
    assert s == t


def test_plaintext():
    t = """Hello, world"""
    s = yy.render(t)
    assert s == t


def test_basic_expr():
    t = '{2+2}=4'
    s = yy.render(t)
    assert s == '4=4'
