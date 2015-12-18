#!/usr/bin/env python

#/***************************************************************************
# *   Copyright (C) 2015 deso (deso@posteo.net)                             *
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

"""A script to replace single quotes with double quotes in a Python file.

  This script can be used to replace all occurrences of single quotes
  with double quotes in a Python file. It does so by invoking the Python
  tokenizer on the file, extracting all string tokens, and replacing the
  introducing and ending quotes. The script touches only true Python
  strings, leaving quotations within them or within comments untouched.
"""


from argparse import (
  ArgumentParser,
)
from os.path import (
  abspath,
)
from re import (
  compile as regex,
)
from sys import (
  argv as sysargv,
)
from token import (
  STRING as TOKEN_STRING,
)
from tokenize import (
  tokenize,
)


# Python has (at least?) two string syntaxes: one with three
# quotation marks (be they single or double) and another with a
# single one (again, a single or double quote sign).
SINGLE_QUOTE = "'"
DOUBLE_QUOTE = "\""
NO_QUOTE = r"[^{sq}{dq}]".format(sq=SINGLE_QUOTE, dq=DOUBLE_QUOTE)
# Create a regular expression that can be used to match a string token.
# TODO: Check the possible prefixes and the maximum number.
STRING = r"({n}?)(?P<quote>{sq}{{3}}|{dq}{{3}}|{sq}|{dq})(.*)(?P=quote)"
STRING = STRING.format(n=NO_QUOTE, sq=SINGLE_QUOTE, dq=DOUBLE_QUOTE)
STRING_RE = regex(STRING)


def fixStrings(file_):
  """Replace all "wrong" strings in a file and return a fixed up list of lines."""
  def readline(*args, **kwargs):
    """Wrapper around the file_'s readline that stores the lines we read."""
    line = file_.readline(*args, **kwargs)
    lines.append(line)
    return line

  def replaceQuotes(string):
    """Replace single quotes with double quotes in a string."""
    def replace(match):
      """Perform the actual replacement."""
      prefix, quotes, quoted = match.groups()
      quotes = quotes.replace(SINGLE_QUOTE, DOUBLE_QUOTE)
      return prefix + quotes + quoted + quotes

    return STRING_RE.sub(replace, string)

  lines = []
  iterator = tokenize(readline)

  for type_, string, _, _, _ in iterator:
    if type_ == TOKEN_STRING:
      replaced = replaceQuotes(string).encode("utf-8")
      lines[-1] = lines[-1].replace(string.encode("utf-8"), replaced, 1)

  return lines


def main(argv):
  """Fix up the (Python) strings in all supplied files."""
  parser = ArgumentParser()
  parser.add_argument(
    "files", action="store", default=[], nargs="+",
    help="A list of files to work on.",
  )

  ns = parser.parse_args(argv[1:])

  for file_ in ns.files:
    file_ = abspath(file_)
    # Note that although we are working with a plain-text Python file we
    # still have to open it in binary mode, otherwise tokenization will
    # fail.
    with open(file_, "rb") as src:
      content = fixStrings(src)

    with open(file_, "wb+") as dst:
      dst.writelines(content)


if __name__ == "__main__":
  main(sysargv)
