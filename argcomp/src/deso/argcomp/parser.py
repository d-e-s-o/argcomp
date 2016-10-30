# parser.py

#/***************************************************************************
# *   Copyright (C) 2016 Daniel Mueller (deso@posteo.net)                   *
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

"""Argument completion functionality for the argparse module."""

from argparse import (
  Action,
  ArgumentParser,
  REMAINDER,
  SUPPRESS,
)
from deso.argcomp.trie import (
  iterWords,
  PrefixNotFound,
  PrefixTree,
)


def complete(prefix_tree, to_complete):
  """Complete the last word in the given list of words."""
  try:
    node = prefix_tree.find(to_complete)
    for word, _ in iterWords(node):
      yield word
  except PrefixNotFound:
    # If no word is matched by the given prefix we have nothing to do.
    pass


class CompleteAction(Action):
  """An action used for completing command line arguments."""
  def __call__(self, parser, namespace, values, option_string=None):
    """Invoke the action to attempt to complete a command line argument."""
    # The values array we got passed in here contains all arguments as
    # they were passed in to the --_complete option, in our case, the
    # word index ($COMP_CWORD) and words as parsed by the shell
    # ($COMP_WORDS[@]). The first word in the words array is typically
    # the Python script invoked. It might not be if the script was
    # invoked by indirectly by passing it as an argument to the
    # interpreter.
    index, script, *words = values
    index = int(index)

    # The approach we take here is to print all completions (separated
    # by a new line symbol) and then exit. The latter step is rather
    # clumsy but then no better solution that requires no additional
    # work on the client side was found.
    completions = list(complete(parser.arguments, words[index - 1]))
    if len(completions) > 0:
      print("\n".join(completions))

    parser.exit(0 if len(completions) > 0 else 1)


class CompletingArgumentParser(ArgumentParser):
  """An ArgumentParser derivate with argument completion support."""
  def __init__(self, *args, prefix_chars=None, fromfile_prefix_chars=None,
               **kwargs):
    """Create an argument parser with argument completion support."""
    assert prefix_chars is None, ("The prefix_chars argument is not "
                                  "supported. Got %s." % prefix_chars)
    assert fromfile_prefix_chars is None, ("The fromfile_prefix_chars "
                                           "argument is not supported. "
                                           "Got %s." % fromfile_prefix_chars)

    self._arguments = PrefixTree()

    # Note that in case the add_help option is true the argment parser
    # will add two arguments -h/--help. Because it uses the add_argument
    # method to do so there is nothing to do special from our side.
    super().__init__(*args, **kwargs)

    self.add_argument(
      "--_complete", action=CompleteAction, complete=False,
      nargs=REMAINDER, help=SUPPRESS,
    )


  def add_argument(self, *args, complete=True, **kwargs):
    """Add an argument to the parser."""
    if complete:
      for arg in args:
        self._arguments.insert(arg, None)

    return super().add_argument(*args, **kwargs)


  @property
  def arguments(self):
    """Retrieve the arguments."""
    return self._arguments
