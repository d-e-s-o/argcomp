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


if __name__ == "__main__":
  main()
