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
import io
import sys

import pytest

requires_py3 = pytest.mark.skipif(sys.version_info < (3,5), reason="Requires Python >= 3.5")

# def check_output(callYasha, *args):
#     # params = dict(
#     #     stdout=subprocess.PIPE,
#     #     stderr=subprocess.STDOUT,
#     #     check=False,
#     #     timeout=2,
#     # )
#     # if 'stdin' in kwargs:
#     #     stdin = kwargs['stdin']
#     #     params['input'] = stdin.encode() if stdin else None

#     return (callYasha(*args), 0)

class NamedBytesIO(io.BytesIO):
    def __init__(self, content: bytes, name: str) -> None:
        super().__init__(content)
        self.name = name

def test_env(tmpdir, callYasha):
    template = tmpdir.join('template.j2')
    template.write("{{ 'POSTGRES_URL' | env('postgresql://localhost') }}")

    out, retcode = callYasha(str(template), '-o-')
    assert retcode == 0
    assert out == 'postgresql://localhost'

    os.environ['POSTGRES_URL'] = 'postgresql://127.0.0.1'
    out, retcode = callYasha(str(template), '-o-')
    assert retcode == 0
    assert out == 'postgresql://127.0.0.1'


@requires_py3
def test_shell(callYasha):
    template = b'{{ "uname" | shell }}'
    out, retcode = callYasha('-', input=NamedBytesIO(template, '<stdin>'))
    assert retcode == 0
    assert out == os.uname().sysname


@requires_py3
def test_subprocess(callYasha):
    template = (
        b'{% set r = "uname" | subprocess %}'
        b'{{ r.stdout.decode() }}'
    )
    out, retcode = callYasha('-', input=NamedBytesIO(template, '<stdin>'))
    assert out.strip() == os.uname().sysname


@requires_py3
def test_subprocess_with_unknown_cmd(callYasha):
    template = b'{{ "unknown_cmd" | subprocess }}'
    out, retcode = callYasha('-', input=NamedBytesIO(template, '<stdin>'))
    assert retcode != 0
    assert 'unknown_cmd: not found' in out


@requires_py3
def test_subprocess_with_unknown_cmd_while_check_is_false(callYasha):
    template = (
        b'{% set r = "unknown_cmd" | subprocess(check=False) %}'
        b'{{ r.returncode > 0 }}'
    )
    out, retcode = callYasha('-', input=NamedBytesIO(template, '<stdin>'))
    assert out == 'True'
