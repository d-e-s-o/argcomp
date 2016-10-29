# testPrefixTree.py

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

"""Test cases for the PrefixTree class."""

from deso.argcomp.trie import (
  PrefixNotFound,
  PrefixTree,
)
from unittest import (
  TestCase,
  main,
)


class TestPrefixTree(TestCase):
  """Tests for the PrefixTree class."""
  def testSingleValueFind(self):
    """Test the finding of true prefixes in a trie with a single element."""
    tree = PrefixTree()
    tree.insert("foo", 42)

    node = tree.find("f")
    self.assertFalse(node.hasValue())
    self.assertEqual(str(node), "f")
    self.assertEqual(len(list(iter(node))), 1)

    node = tree.find("fo")
    self.assertFalse(node.hasValue())
    self.assertEqual(str(node), "fo")
    self.assertEqual(len(list(iter(node))), 1)

    node = tree.find("foo")
    # This time the node must have a value.
    self.assertTrue(node.hasValue())
    self.assertEqual(node.value, 42)
    self.assertEqual(str(node), "foo")
    self.assertEqual(len(list(iter(node))), 0)


  def testMultiValueFind(self):
    """Test the finding of true prefixes in a trie with multiple elements."""
    tree = PrefixTree()
    tree.insert("foo", 42)
    tree.insert("bar", 0xdeadbeef)
    tree.insert("foobar", 1337)
    tree.insert("baz", 0xdead)
    tree.insert("boo", "value")

    node = tree.find("f")
    self.assertFalse(node.hasValue())
    self.assertEqual(str(node), "f")
    self.assertEqual(len(list(iter(node))), 1)

    node = tree.find("foo")
    self.assertTrue(node.hasValue())
    self.assertEqual(node.value, 42)
    self.assertEqual(str(node), "foo")
    self.assertEqual(len(list(iter(node))), 1)

    node = tree.find("b")
    self.assertFalse(node.hasValue())
    self.assertEqual(str(node), "b")
    self.assertEqual(len(list(iter(node))), 2)

    node = tree.find("ba")
    self.assertFalse(node.hasValue())
    self.assertEqual(str(node), "ba")
    self.assertEqual(len(list(iter(node))), 2)

    node = tree.find("bo")
    self.assertFalse(node.hasValue())
    self.assertEqual(str(node), "bo")
    self.assertEqual(len(list(iter(node))), 1)


  def testNoTruePrefixFound(self):
    """Verify that the find() method fails as expected."""
    tree = PrefixTree()

    with self.assertRaises(PrefixNotFound):
      tree.find("a")

    tree.insert("boo", object())

    with self.assertRaises(PrefixNotFound):
      tree.find("booz")

    with self.assertRaises(PrefixNotFound):
      tree.find("foo")


  def testFindExact(self):
    """Test the search for exact strings in a PrefixTree."""
    tree = PrefixTree()
    tree.insert("foo", None)
    tree.insert("foobar", 1337)

    node = tree.findExact("foo")
    self.assertTrue(node.hasValue())
    self.assertEqual(str(node), "foo")
    self.assertEqual(len(list(iter(node))), 1)

    node = tree.findExact("foobar")
    self.assertTrue(node.hasValue())
    self.assertEqual(str(node), "foobar")
    self.assertEqual(len(list(iter(node))), 0)


  def testNoExactStringFound(self):
    """Verify that the findExact() method fails as expected."""
    tree = PrefixTree()

    with self.assertRaises(PrefixNotFound):
      tree.findExact("f")

    tree.insert("baz", {"a": 1})

    with self.assertRaises(PrefixNotFound):
      tree.findExact("ba")

    with self.assertRaises(PrefixNotFound):
      tree.find("bazr")

    tree.insert("bar", None)

    with self.assertRaises(PrefixNotFound):
      tree.findExact("ba")


if __name__ == "__main__":
  main()
