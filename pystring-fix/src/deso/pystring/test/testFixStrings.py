#!/usr/bin/env python

#/***************************************************************************
# *   Copyright (C) 2015-2016 deso (deso@posteo.net)                        *
# *                                                                         *
# *   This program is free software: you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation, either version 3 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU General Public License for more details.                          *
# *                                                                         *
# *   You should have received a copy of the GNU General Public License     *
# *   along with this program.  If not, see <http://www.gnu.org/licenses/>. *
# ***************************************************************************/

"""Tests for the Python string unification script."""

from deso.pystring import (
  fixStrings,
)
from tempfile import (
  NamedTemporaryFile,
)
from textwrap import (
  dedent,
)
from unittest import (
  main,
  TestCase,
)


class TestFixStrings(TestCase):
  """Tests for the Python string unification functionality."""
  def doTest(self, content, expected):
    """Fix the strings in a Python file and verify the expected outcome."""
    with NamedTemporaryFile("w+b", buffering=0) as f:
      f.write(content)
      f.seek(0)

      new_content = fixStrings(f)
      f.truncate()
      f.seek(0)

      f.write(new_content)
      f.seek(0)

      self.assertEqual(f.read(), expected)


  def testSingleLineUnification(self):
    """Verify that single line Python strings are unified properly."""
    content = dedent("""\
      'foo'
      "foo"
      b'foo'
      b'''foo'''
      r'foo'
      r'''foo'''
      b"foo"
      b\"\"\"foo\"\"\"
      r"foo"
      r\"\"\"foo\"\"\"
      '''Foo 'bar' foobar.'''
      \"\"\"Foo 'bar' foobar.\"\"\"
      # That's a "test"
      # 'That's a "test"'
      # 'That's a 'test' in a comment'
    """).encode("utf-8")

    expected = dedent("""\
      "foo"
      "foo"
      b"foo"
      b\"\"\"foo\"\"\"
      r"foo"
      r\"\"\"foo\"\"\"
      b"foo"
      b\"\"\"foo\"\"\"
      r"foo"
      r\"\"\"foo\"\"\"
      \"\"\"Foo 'bar' foobar.\"\"\"
      \"\"\"Foo 'bar' foobar.\"\"\"
      # That's a "test"
      # 'That's a "test"'
      # 'That's a 'test' in a comment'
    """).encode("utf-8")

    self.doTest(content, expected)


  def testMultiLineUnification(self):
    """Verify that multi-line Python strings are unified properly."""
    content = dedent("""\
      script = bytes(dedent('''
        pid = fork()
        if pid == 0:
          print('CHILD')
        else:
          print('PARENT')
      '''), 'utf-8')
    """).encode("utf-8")

    expected = dedent("""\
      script = bytes(dedent(\"\"\"
        pid = fork()
        if pid == 0:
          print('CHILD')
        else:
          print('PARENT')
      \"\"\"), "utf-8")
    """).encode("utf-8")

    self.doTest(content, expected)


if __name__ == "__main__":
  main()
