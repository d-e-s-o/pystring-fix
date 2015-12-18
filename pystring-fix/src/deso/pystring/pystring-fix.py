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
from sys import (
  argv as sysargv,
)
from token import (
  STRING,
)
from tokenize import (
  tokenize,
)


def fixStrings(file_):
  """Replace all "wrong" strings in a file and return a fixed up list of lines."""
  def readline(*args, **kwargs):
    """Wrapper around the file_'s readline that stores the lines we read."""
    line = file_.readline(*args, **kwargs)
    lines.append(line)
    return line

  def checkAndReplace(string, old, new):
    """Check if a replacement in the last line is required and, if so, do it."""
    index = string.find(old)
    rindex = string.rfind(old)

    if index >= 0 and rindex >= 0 and index != rindex:
      # Unfortunately the tokenizer supplies us with a true string
      # although in all other places we work bytes like objects. So
      # in case we need to make a replacement we need to convert the
      # string first.
      bytes_ = string.encode("utf-8")
      new = new.encode("utf-8")

      # We need to consider that a prefix might be placed in front of
      # the string. That is what the first part is for.
      replacement = bytes_[0:index] +\
                    new +\
                    bytes_[index+len(old):rindex] +\
                    new
      lines[-1] = lines[-1].replace(bytes_, replacement, 1)
      return True

    return False

  lines = []
  iterator = tokenize(readline)

  for type_, string, _, _, _ in iterator:
    if type_ == STRING:
      # Python has (at least?) two string syntaxes: one with three
      # quotation marks (be they single or double) and another with a
      # single one (again, a single or double quote sign).
      if not checkAndReplace(string, "'''", "\"\"\""):
        checkAndReplace(string, "'", "\"")

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
