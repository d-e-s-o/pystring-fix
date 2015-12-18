# __init__.py

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

"""Properly faceded imports for the git.subrepo module."""

# The symbol names to export.
to_import = [
  "fixStrings",
]

# Import the desired names from the git-subrepo file. Because a dash is
# contained in the name, we have to make some hand stands to export the
# proper symbols from the script as part of the module.
subrepo = __import__("deso.pystring.pystring-fix", globals(), locals(), to_import)
globals().update({k: getattr(subrepo, k) for k in to_import})
del subrepo
