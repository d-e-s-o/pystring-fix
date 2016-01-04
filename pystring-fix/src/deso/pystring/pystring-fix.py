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
  DOTALL,
)
from sys import (
  argv as sysargv,
  stderr,
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
STRING_RE = regex(STRING, DOTALL)


def fixStrings(file_):
  """Replace all "wrong" strings in a file and return the fixed up content."""
  def readline(*args, **kwargs):
    """Wrapper around the file_'s readline that stores the content we read so far."""
    line = file_.readline(*args, **kwargs)
    content[0] += line
    return line

  def replaceQuotes(string):
    """Replace single quotes with double quotes in a string."""
    def replace(match):
      """Perform the actual replacement."""
      prefix, quotes, quoted = match.groups()
      quotes = quotes.replace(SINGLE_QUOTE, DOUBLE_QUOTE)
      return prefix + quotes + quoted + quotes

    return STRING_RE.sub(replace, string)

  def rreplace(string, to_replace, replacement):
    """Replace the last occurrence of 'to_replace' with 'replacement'."""
    begin = string.rindex(to_replace)
    end = begin + len(to_replace)

    return string[:begin] + replacement + string[end:]

  # We need a mutable object here so that it can be captured in the
  # 'readline' function. That's why we use a list containing a single
  # bytes object.
  content = [b""]
  iterator = tokenize(readline)

  for type_, string, _, _, _ in iterator:
    if type_ == TOKEN_STRING:
      replaced = replaceQuotes(string).encode("utf-8")
      content[0] = rreplace(content[0], string.encode("utf-8"), replaced)

  return content[0]


def main(argv):
  """Fix up the (Python) strings in all supplied files."""
  parser = ArgumentParser()
  parser.add_argument(
    "files", action="store", default=[], nargs="+",
    help="A list of files to work on.",
  )
  parser.add_argument(
    "-c", "--check", action="store_true", default=False,
    help="Only check the given files for inconsistent quotation usage, "
         "do not correct them.",
  )

  ns = parser.parse_args(argv[1:])

  for file_ in ns.files:
    file_ = abspath(file_)
    # Note that although we are working with a plain-text Python file we
    # still have to open it in binary mode, otherwise tokenization will
    # fail.
    with open(file_, "rb") as src:
      content = fixStrings(src)

      if ns.check:
        src.seek(0)
        if content != src.read():
          print("Inconsistent quotation usage detected in %s." % file_,
                file=stderr)
          return 1

    if not ns.check:
      with open(file_, "wb+") as dst:
        dst.write(content)

  return 0


if __name__ == "__main__":
  exit(main(sysargv))
