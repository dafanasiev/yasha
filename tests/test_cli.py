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

import pytest
from os import path, chdir
import subprocess
from subprocess import check_output

@pytest.fixture(params=('json', 'yaml', 'yml', 'toml'))
def vartpl(request):
    template = {
        'json': '{{"int": {int}}}',
        'yaml': 'int: {int}',
        'yml': 'int: {int}',
        'toml': 'int={int}',
    }
    fmt = request.param  # format
    return (template[fmt], fmt)


@pytest.fixture
def varfile(vartpl, tmpdir):
    content = {'int': 1}
    template, filext = vartpl
    file = tmpdir.join('variables.{}'.format(filext))
    file.write(template.format(**content))
    return file


def test_explicit_variable_file(tmpdir, varfile, callYasha):
    tpl = tmpdir.join('template.j2')
    tpl.write('{{ int }}')

    _, errno = callYasha('-v', str(varfile), str(tpl))
    assert errno == 0

    output = tmpdir.join('template')
    assert output.read() == '1'


def test_two_explicitly_given_variables_files(tmpdir, callYasha):
    # Template to calculate a + b + c:
    tpl = tmpdir.join('template.j2')
    tpl.write('{{ a + b + c }}')

    # First variable file defines a & b:
    a = tmpdir.join('a.yaml')
    a.write('a: 1\nb: 100')

    # Second variable file redefines b & defines c:
    b = tmpdir.join('b.toml')
    b.write('b = 2\nc = 3')

    _, errno = callYasha('-v', str(a), '-v', str(b), str(tpl))
    assert errno == 0

    output = tmpdir.join('template')
    assert output.read() == '6'  # a + b + c = 1 + 2 + 3 = 6


def test_variable_file_lookup(tmpdir, vartpl, callYasha):
    # /cwd
    #   /sub
    #     foo.c.j2
    cwd = tmpdir.chdir()
    tpl = tmpdir.mkdir('sub').join('foo.c.j2')
    tpl.write('int x = {{ int }};')

    # /cwd
    #   /sub
    #     foo.c.j2
    #     foo.c.json    int = 2
    #     foo.json      int = 1
    #   foo.json        int = 0
    for i, varfile in enumerate(('foo', 'sub/foo', 'sub/foo.c')):
        varfile += '.' + vartpl[1]
        varfile = tmpdir.join(varfile)
        varfile.write(vartpl[0].format(int=i))

        _, errno = callYasha('sub/foo.c.j2')
        assert errno == 0
        assert path.isfile('sub/foo.c')

        output = tmpdir.join('sub/foo.c')
        assert output.read() == 'int x = {};'.format(i)

def test_custom_xmlparser(tmpdir, callYasha):
    template = """
    {% for p in persons %}
    [[persons]]
    name = "{{ p.name }}"
    address = "{{ p.address }}"
    {% endfor %}"""

    variables = """
    <persons>
        <person>
            <name>Foo</name>"
            <address>Foo Valley</address>
        </person>
        <person>
            <name>Bar</name>
            <address>Bar Valley</address>
        </person>
    </persons>
    """

    extensions = """
def parse_xml(file):
    import xml.etree.ElementTree as et
    tree = et.parse(file.name)
    root = tree.getroot()
    variables = {"persons": []}
    for elem in root.iter("person"):
        variables["persons"].append({
            "name": elem.find("name").text,
            "address": elem.find("address").text,
        })
    return variables
    """

    cwd = tmpdir.chdir()

    file = tmpdir.join("foo.xml")
    file.write(variables)

    file = tmpdir.join("foo.toml.jinja")
    file.write(template)

    file = tmpdir.join("foo.j2ext")
    file.write(extensions)

    _, errno = callYasha("foo.toml.jinja")
    assert errno == 0
    assert path.isfile("foo.toml")

    o = tmpdir.join("foo.toml")
    assert o.read() == """
    [[persons]]
    name = "Foo"
    address = "Foo Valley"
    [[persons]]
    name = "Bar"
    address = "Bar Valley"\n"""


def test_broken_extensions(tmpdir, callYasha):
    from subprocess import CalledProcessError, STDOUT
    tmpdir.chdir()

    extensions = """def foo()
    return "foo"
    """

    tpl = tmpdir.join("foo.jinja")
    tpl.write("")

    ext = tmpdir.join("foo.j2ext")
    ext.write(extensions)

    out, errcode = callYasha("foo.jinja")
    assert errcode == 1
    assert "Invalid syntax (foo.j2ext, line 1)" in out


def test_broken_extensions_name_error(tmpdir, callYasha):
    from subprocess import CalledProcessError, STDOUT
    tmpdir.chdir()

    extensions = "asd"

    tpl = tmpdir.join("foo.jinja")
    tpl.write("")

    ext = tmpdir.join("foo.j2ext")
    ext.write(extensions)

    out, errcode = callYasha("foo.jinja")
    assert errcode == 1
    assert "name 'asd' is not defined" in out


def test_render_template_from_stdin_to_stdout(src_dir):
    cmd = r'echo -n "{{ foo }}" | pipenv run python3 -m yasha --foo=bar -'
    out = check_output(cmd, shell=True, cwd=src_dir)
    assert out == b'bar'


def test_json_template(tmpdir, callYasha):
    """gh-34, and gh-35"""
    tmpdir.chdir()

    tmpl = tmpdir.join('template.json')
    tmpl.write('{"foo": {{\'"%s"\'|format(bar)}}}')

    out, _ = callYasha('--bar=baz', '-o-', 'template.json')
    assert out == '{"foo": "baz"}'


def test_mode_is_none(src_dir):
    """gh-42, and gh-44"""
    cmd = r'echo -n "{{ foo }}" | pipenv run python3 -m yasha -'
    out = check_output(cmd, shell=True, cwd=src_dir)
    assert out == b''


def test_mode_is_pedantic(src_dir):
    """gh-42, and gh-48"""
    import os
    with pytest.raises(subprocess.CalledProcessError) as err:
        cmd = r'echo -n "{{ foo }}" | pipenv run python3 -m yasha --mode=pedantic -'
        out = check_output(cmd, shell=True, stderr=subprocess.STDOUT, cwd=src_dir)
    out = err.value.output
    assert out == b"Error: Variable 'foo' is undefined\n"


def test_mode_is_debug(src_dir):
    """gh-44"""
    cmd = r'echo -n "{{ foo }}" | pipenv run python3 -m yasha --mode=debug -'
    out = check_output(cmd, shell=True, cwd=src_dir)
    assert out == b'{{ foo }}'


def test_template_syntax_for_latex(tmpdir, callYasha):
    """gh-43"""
    template = r"""
\begin{itemize}
<% for x in range(0, 3) %>
    \item Counting: << x >>
<% endfor %>
\end{itemize}
"""

    extensions = r"""
BLOCK_START_STRING = '<%'
BLOCK_END_STRING = '%>'
VARIABLE_START_STRING = '<<'
VARIABLE_END_STRING = '>>'
COMMENT_START_STRING = '<#'
COMMENT_END_STRING = '#>'
"""

    expected_output = r"""
\begin{itemize}
    \item Counting: 0
    \item Counting: 1
    \item Counting: 2
\end{itemize}
"""

    tpl = tmpdir.join('template.tex')
    tpl.write(template)

    ext = tmpdir.join('extensions.py')
    ext.write(extensions)

    out, _ = callYasha('-e', str(ext), '-o-', str(tpl))
    assert out == expected_output


def test_extensions_file_with_do(tmpdir, callYasha):
    """gh-52"""
    tmpdir.chdir()

    extensions = tmpdir.join('extensions.py')
    extensions.write('from jinja2.ext import do')

    tmpl = tmpdir.join('template.j2')
    tmpl.write(r'{% set list = [1, 2, 3] %}{% do list.append(4) %}{{ list }}')

    out,_ = callYasha('-e', str(extensions), '-o-', str(tmpl))
    assert out == '[1, 2, 3, 4]'
