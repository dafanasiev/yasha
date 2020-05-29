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

import sys
import pytest
import os.path

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
SRC_DIR = os.path.dirname(SCRIPT_PATH)

sys.path.append(SRC_DIR)

@pytest.fixture
def src_dir():
    return SRC_DIR

@pytest.fixture
def fixtures_dir():
    return os.path.join(SCRIPT_PATH, "fixtures")



@pytest.fixture
def callYasha():
    from yasha import cli
    from click.testing import CliRunner

    def caller(*args, **kvargs):
        runner = CliRunner()
        result = runner.invoke(cli, args=args, **kvargs)
        return result.output, result.exit_code
    return caller
