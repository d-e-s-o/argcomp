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
from itertools import (
  chain,
)
from sys import (
  argv,
)


COMPLETE_OPTION = "--_complete"


def escapeDoubleDash(args, index=0):
  """Escape all '--' strings in the array."""
  first = args[:index]
  second = map(lambda x: x.replace(r"--", r"\--"), args[index:])
  return chain(first, second)


def unescapeDoubleDash(args):
  """Unescape all escaped '--' strings in the array."""
  return map(lambda x: x.replace(r"\--", r"--"), args)


def complete(prefix_tree, words):
  """Complete the last word in the given list of words."""
  # Without loss of generality, we attempt completing the last word in
  # the list of words. The assumption here is that only context before
  # this word matters, so everything found afterwards is irrelevant and
  # must be removed by the caller.
  *words, to_complete = words
  try:
    for word in words:
      node = prefix_tree.findExact(word)
      if node.hasValue():
        value = node.value
        if isinstance(value, PrefixTree):
          prefix_tree = value

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
    values = list(unescapeDoubleDash(values))

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
    completions = list(complete(parser.arguments, words[:index]))
    if len(completions) > 0:
      print("\n".join(completions))

    parser.exit(0 if len(completions) > 0 else 1)


class CompletingArgumentParser(ArgumentParser):
  """An ArgumentParser derivate with argument completion support."""
  def __init__(self, *args, prefix_chars=None, fromfile_prefix_chars=None,
               arguments=None, **kwargs):
    """Create an argument parser with argument completion support."""
    assert prefix_chars is None, ("The prefix_chars argument is not "
                                  "supported. Got %s." % prefix_chars)
    assert fromfile_prefix_chars is None, ("The fromfile_prefix_chars "
                                           "argument is not supported. "
                                           "Got %s." % fromfile_prefix_chars)

    if arguments is None:
      self._arguments = PrefixTree()
    else:
      self._arguments = arguments

    # Note that in case the add_help option is true the argment parser
    # will add two arguments -h/--help. Because it uses the add_argument
    # method to do so there is nothing to do special from our side.
    super().__init__(*args, **kwargs)

    self.add_argument(
      COMPLETE_OPTION, action=CompleteAction, complete=False,
      nargs=REMAINDER, help=SUPPRESS,
    )


  def add_argument(self, *args, complete=True, **kwargs):
    """Add an argument to the parser."""
    if complete:
      for arg in args:
        self._arguments.insert(arg, None)

    return super().add_argument(*args, **kwargs)


  def parse_args(self, args=None, namespace=None):
    """Parse a list of arguments."""
    if args is None:
      args = argv[1:]

    # Unfortunately, any '--' argument is interpreted by the
    # ArgumentParser causing it to treat all follow up arguments as
    # positional ones. This behavior is undesired for the --_complete
    # option where '--' is a valid prefix of an argument to complete and
    # so we escape it here (and unescape it later).
    # Alternatively, we could use two other approaches:
    # 1) Pass in the entire line instead of a pre-split list of words as
    #    provided by the $COMP_WORDS shell variable. The downside here
    #    is that we would manually need to perform argument
    #    parsing/splitting here (which is what we want to avoid, even in
    #    the face of the shlex module).
    # 2) Do not pass in arguments to --_complete but rather treat
    #    everything else as positional arguments. With this approach we
    #    have to find a way to define those (optional!) positional
    #    arguments but also to pass them in to the CompleteAction.
    try:
      # TODO: This approach likely breaks assignments, e.g.,
      #       --_complete="${COMP_WORDS[@]}"
      index = args.index(COMPLETE_OPTION) + 1
      args = list(escapeDoubleDash(args, index=index))
    except ValueError:
      pass

    return super().parse_args(args=args, namespace=namespace)


  def add_subparsers(self, *args, **kwargs):
    """Add subparsers to the argument parser."""
    def addParser(add_parser, name, *args, **kwargs):
      """A replacement method for the add_parser method."""
      sub_arguments = PrefixTree()
      self._arguments.insert(name, sub_arguments)

      # Invoke the original add_parser function. We need to do that
      # because this function takes care of handling special keyword
      # arguments such as 'help' which must not be passed through to our
      # argument parser directly.
      return add_parser(name, *args, arguments=sub_arguments, **kwargs)

    assert "parser_class" not in kwargs, ("parser_class argument not supported. "
                                          "Got %s." % kwargs["parser_class"])

    # We create the subparsers object as would be done by a "real"
    # ArgumentParser but also overwrite the add_parser method.
    subparsers = super().add_subparsers(*args, parser_class=CompletingArgumentParser, **kwargs)

    add_parser = subparsers.add_parser
    subparsers.add_parser = lambda *a, **k: addParser(add_parser, *a, **k)

    return subparsers


  @property
  def arguments(self):
    """Retrieve the arguments."""
    return self._arguments
