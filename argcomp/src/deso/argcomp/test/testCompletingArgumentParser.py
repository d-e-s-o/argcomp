# testCompletingArgumentParser.py

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

"""Tests for the CompletingArgumentParser class."""

from deso.argcomp import (
  CompletingArgumentParser,
)
from deso.argcomp.parser import (
  escapeDoubleDash,
  unescapeDoubleDash,
)
from io import (
  StringIO,
)
from sys import (
  argv as sysargv,
  executable,
)
from unittest import (
  TestCase,
  main,
)
from unittest.mock import (
  patch,
)


class TestMisc(TestCase):
  """Tests for miscellaneous functionality accompanying the argument parser."""
  def testEscape(self):
    """Test the escapeDoubleDash function."""
    escaped = escapeDoubleDash([r"--"])
    self.assertEqual(list(escaped), [r"\--"])


  def testEscapeFromIndex(self):
    """Test the escapeDoubleDash function with a start index."""
    # No escaping should occur if we start at the second element.
    args = [r"--", r"foo"]
    escaped = escapeDoubleDash(args, 1)
    self.assertEqual(list(escaped), [r"--", r"foo"])


  def testEscapeAndUnescape(self):
    """Verify that escaping and unescaping an argument vector results in the original."""
    args = [r"bar", r"\\--", r"\--", r"--", r"--fo", r"foo"]
    transformed = unescapeDoubleDash(escapeDoubleDash(args))
    self.assertEqual(list(transformed), args)


class TestCompletingArgumentParser(TestCase):
  """Test cases for the CompletingArgumentParser class."""
  def performCompletion(self, parser, to_complete, expected, exit_code=0):
    """Attempt a completion and compare the result against the expectation."""
    argv = [
      executable,
      __file__,
      "--_complete",
      # For now we always complete the second argument (argument indices
      # are zero based).
      "%d" % len(to_complete),
      sysargv[0],
    ] + to_complete

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
      # After performing a completion we expect the parser to exit but
      # we want to avoid an exit for testing purposes.
      with self.assertRaises(SystemExit) as e:
        parser.parse_args(argv[2:])

      completions = set(mock_stdout.getvalue().splitlines())
      self.assertSetEqual(completions, expected)
      self.assertEqual(e.exception.code, exit_code)


  def testSimpleKeywordArguments(self):
    """Verify that simple keyword arguments can be completed properly."""
    parser = CompletingArgumentParser(prog="foo", add_help=False)

    parser.add_argument("--foo", action="store_true")
    self.performCompletion(parser, ["-"], {"--foo"})

    parser.add_argument("-b", "--bar", action="store_true")
    self.performCompletion(parser, ["-"], {"--foo", "-b", "--bar"})
    self.performCompletion(parser, ["--"], {"--foo", "--bar"})
    self.performCompletion(parser, ["-b"], {"-b"})
    self.performCompletion(parser, ["-b", "--foo", "-b"], {"-b"})
    self.performCompletion(parser, ["-b", "--foo", ""], {"--foo", "-b", "--bar"})

    # Also verify that an error is reported if there is no matching
    # completion.
    self.performCompletion(parser, ["--var"], set(), exit_code=1)
    self.performCompletion(parser, ["-z"], set(), exit_code=1)
    self.performCompletion(parser, ["-b", "-a"], set(), exit_code=1)


  def testHelpCompletion(self):
    """Verify that the -h/--help arguments can be completed properly."""
    parser = CompletingArgumentParser(prog="foo")
    parser.add_argument("--foo", action="store_true")

    self.performCompletion(parser, ["-"], {"-h", "--foo", "--help"})
    self.performCompletion(parser, ["--h"], {"--help"})


  def testCompletionWithSubparser(self):
    """Verify that completion also works with sub parsers."""
    parser = CompletingArgumentParser(prog="subfoo", add_help=False)
    parser.add_argument("--foo", action="store_true")

    subparsers = parser.add_subparsers()
    bar = subparsers.add_parser("bar", add_help=False)
    bar.add_argument("-b", "--baz", action="store_true")

    foobar = subparsers.add_parser("foobar")
    foobar.add_argument("--foobar", action="store_true")

    subparsers2 = foobar.add_subparsers()
    foobarbaz = subparsers2.add_parser("foobarbaz", add_help=False)
    foobarbaz.add_argument("--test", action="store_true")

    self.performCompletion(parser, ["-"], {"--foo"})
    self.performCompletion(parser, ["b"], {"bar"})
    self.performCompletion(parser, ["bar", ""], {"-b", "--baz"})
    self.performCompletion(parser, ["foobar", ""], {"foobarbaz", "-h", "--foobar", "--help"})
    self.performCompletion(parser, ["--foo", "foobar", ""], {"foobarbaz", "-h", "--foobar", "--help"})
    self.performCompletion(parser, ["foobar", "--f"], {"--foobar"})
    self.performCompletion(parser, ["foobar", "f"], {"foobarbaz"})
    self.performCompletion(parser, ["foobar", "--foobar", "foobarbaz", ""], {"--test"})
    self.performCompletion(parser, ["--foo", "foobar", "foobarbaz", ""], {"--test"})


  def testSubparsersCanCompleteSubCommands(self):
    """Verify that sub parsers can complete arguments themselves."""
    root = CompletingArgumentParser(prog="root", add_help=False)
    root.add_argument("--rootopt", action="store_true")

    subparsers = root.add_subparsers()
    sub1 = subparsers.add_parser("sub1", add_help=False, help="Perform sub1.")
    sub1.add_argument("-s", "--sub1opt", action="store_true")

    sub2 = subparsers.add_parser("sub2", add_help=False)
    sub2.add_argument("-s", "--sub2opt", action="store_true")

    subparsers2 = sub2.add_subparsers()
    sub21 = subparsers2.add_parser("sub21", help="Perform sub21.")
    sub21.add_argument("--sub21opt", action="store_true")

    self.performCompletion(root, [""], {"--rootopt", "sub1", "sub2"})
    self.performCompletion(sub1, [""], {"-s", "--sub1opt"})
    self.performCompletion(sub1, ["--"], {"--sub1opt"})
    self.performCompletion(sub2, [""], {"sub21", "-s", "--sub2opt"})
    self.performCompletion(sub21, [""], {"-h", "--help", "--sub21opt"})


if __name__ == "__main__":
  main()
