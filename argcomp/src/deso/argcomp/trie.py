# trie.py

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

"""An implementation of a prefix tree."""


def iterWords(node):
  """Iterate over the actual words in a PrefixTree."""
  if node.hasValue():
    yield str(node), node.value

  for child in iter(node):
    for prefix, value in iterWords(child):
      yield prefix, value


class PrefixNotFound(Exception):
  """An exception indicating that no entry was found beginning with the given prefix."""
  pass


class _Node:
  """A client accessible node in a PrefixTree."""
  def __init__(self, prefix, node):
    """Initialize the node object."""
    self._prefix = prefix
    self._node = node


  def __iter__(self):
    """Iterate over the node's children."""
    for char, node in self._node.items():
      # The "value" key is special in that it is used to hold the actual
      # value. It must not be exposed to clients.
      if char == "value":
        continue

      yield _Node(self._prefix + char, node)


  def __str__(self):
    """Retrieve the prefix the node represents."""
    return self._prefix


  def hasValue(self):
    """Check whether the node has a value."""
    return "value" in self._node


  @property
  def value(self):
    """Retrieve this node's value.

      If the node has no value (i.e., hasValue returns False) then the
      behavior is undefined.
    """
    return self._node["value"]


class PrefixTree:
  """A class representing a prefix tree."""
  def __init__(self):
    """Initialize an empty prefix tree object."""
    self._tree = {}


  def _getNode(self, prefix, insert=False):
    """Retrieve the node for a given prefix."""
    node = self._tree
    used = str()

    for char in prefix:
      if char in node:
        next_node = node[char]
      else:
        if not insert:
          raise PrefixNotFound("Prefix %s not found." % prefix)

        next_node = {}
        node[char] = next_node

      node = next_node
      used += char

    return used, node


  def insert(self, word, value):
    """Insert a value associated with the given word into the tree."""
    _, node = self._getNode(word, insert=True)
    node["value"] = value


  def find(self, prefix):
    """Find the node representing the longest word containing the given prefix."""
    prefix, node = self._getNode(prefix)
    # We create nodes lazily.
    return _Node(prefix, node)


  def findExact(self, string):
    """Find the node matching the given string, if any."""
    node = self.find(string)
    if str(node) != string or not node.hasValue():
      raise PrefixNotFound("String %s not found." % string)

    return node


  @property
  def root(self):
    """Retrieve the root node of the tree."""
    return _Node(str(), self._tree)
