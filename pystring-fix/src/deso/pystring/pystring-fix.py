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
SINGLE_QUOTE_B = SINGLE_QUOTE.encode("utf-8")
DOUBLE_QUOTE_B = DOUBLE_QUOTE.encode("utf-8")
NO_QUOTE = r"[^{sq}{dq}]".format(sq=SINGLE_QUOTE, dq=DOUBLE_QUOTE)
# Create a regular expression that can be used to match a string token.
# TODO: Check the possible prefixes and the maximum number.
STRING = r"({n}?)(?P<quote>{sq}{{3}}|{dq}{{3}}|{sq}|{dq})(.*)(?P=quote)"
STRING = STRING.format(n=NO_QUOTE, sq=SINGLE_QUOTE, dq=DOUBLE_QUOTE)
STRING_RE = regex(STRING.encode("utf-8"), DOTALL)


class QuotationUnifier:
  """A class for replacing single quotes with double quotes."""
  def __init__(self):
    """Create and initialize a quotation mark unification object."""
    # A buffer of all the data we got fed so far.
    self._buffer = b""
    # Array of indexes at which the respective lines end.
    self._indexes = []


  def feed(self, line):
    """Feed a new line to the unifier."""
    self._buffer += line
    index = len(line)

    # To avoid unnecessary computation for every replacement/lookup we
    # make we cache the accumulated lenghts of all lines (which equal
    # the indexes at which they end).
    if len(self._indexes) > 0:
      index += self._indexes[-1]

    self._indexes += [index]


  def unify(self, string, start, end):
    """Unify a given string in the internal buffer."""
    def replaceQuotes(s):
      """Replace single quotes with double quotes in a string."""
      def replace(match):
        """Perform the actual replacement."""
        prefix, quotes, quoted = match.groups()
        quotes = quotes.replace(SINGLE_QUOTE_B, DOUBLE_QUOTE_B)
        return prefix + quotes + quoted + quotes

      replaced, count = STRING_RE.subn(replace, s)
      assert count in [0, 1], (s, replaced, count)
      return replaced

    def index(pair):
      """Retrieve the index in the internal buffer for a particular (row,col) tuple."""
      # A pair comprises the row and the column of a string.
      row, col = pair
      # The first actual row of interest is the one numbered one. So
      # normalize to zero here.
      index = row - 1

      # The element at the first index in the array contains the length
      # of the first line. So we need to subtract one more from the
      # index and then use that in order to retrieve the correct
      # position.
      if index < 1:
        return col
      else:
        return self._indexes[index - 1] + col

    index_start = index(start)
    index_end = index(end)

    to_replace = self._buffer[index_start:index_end]
    assert string == to_replace, (string, to_replace, self._buffer)

    replaced = replaceQuotes(to_replace)
    assert len(to_replace) == len(replaced), (to_replace, replaced)

    self._buffer = self._buffer[:index_start] +\
                   replaced +\
                   self._buffer[index_end:]


  @property
  def data(self):
    """Retrieve the "unified" buffer."""
    return self._buffer


def fixStrings(file_):
  """Replace all "wrong" strings in a file and return the fixed up content."""
  def readline(*args, **kwargs):
    """Wrapper around the file_'s readline that stores the content we read so far."""
    line = file_.readline(*args, **kwargs)
    unifier.feed(line)
    return line

  unifier = QuotationUnifier()
  iterator = tokenize(readline)

  for type_, string, start, end, _ in iterator:
    if type_ == TOKEN_STRING:
      unifier.unify(string.encode("utf-8"), start, end)

  return unifier.data


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
