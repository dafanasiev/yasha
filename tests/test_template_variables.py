"""
The MIT License (MIT)

Copyright (c) 2015-2017 Kim Blomqvist

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os
import pytest

@pytest.fixture()
def t(tmpdir):
    return tmpdir.join('template.j2')

def test_string(t, callYasha):
    t.write('{{ var is string }}, {{ var }}')
    out, _ = callYasha('--var', 'foo', '-o-', str(t))
    assert out == 'True, foo'

    t.write('{{ var is string }}, {{ var }}')
    out, _ = callYasha('--var', "'foo'", '-o-', str(t))
    assert out == "True, foo"

def test_boolean(t, callYasha):
    t.write('{{ var is sameas false }}, {{ var }}')
    out, _ = callYasha('--var', 'False', '-o-', str(t))
    assert out == 'True, False'


def test_number(t, callYasha):
    t.write('{{ var is number }}, {{ var + 1 }}')
    out, _ = callYasha('--var', '1', '-o-', str(t))
    assert out == 'True, 2'


def test_list(t, callYasha):
    t.write('{{ var is sequence }}, {{ var | join }}')
    out, _ = callYasha('--var', "['foo', 'bar', 'baz']", '-o-', str(t))
    assert out == 'True, foobarbaz'


def test_tuple(t, callYasha):
    t.write('{{ var is sequence }}, {{ var | join }}')
    out, _ = callYasha('--var', "('foo', 'bar', 'baz')", '-o-', str(t))
    assert out == 'True, foobarbaz'

def test_dictionary(t, callYasha):
    t.write("{{ var is mapping }}, {% for k in 'abc' %}{{ var[k] }}{% endfor %}")
    out, _ = callYasha('--var', "{'a': 1, 'b': 2, 'c': 3}", '-o-', str(t))
    assert out == 'True, 123'
