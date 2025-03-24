"""Tests for Node module."""

from ludo.node import Node, NodeType
from ludo.token import Token
from ludo.house import HouseType
import pytest
from test.utils import DummyHouse


def test_node_has_next_node():
    """Each node must always have a next node."""
    node = Node()
    node.next_node = Node()

    assert node.next_node is not None


def test_start_node_is_safe_node():
    """Initialize the start Node with a unique id and safe type of node."""
    node = Node(NodeType.START)

    assert node.is_safe


def test_general_node_is_unsafe_node():
    """Initialize the general Node with a unique id and unsafe type of node."""
    node = Node(NodeType.REGULAR)

    assert node.is_safe is False


def test_star_node_is_safe_node():
    """Initialize the star Node with a unique id and safe type of node."""
    node = Node(NodeType.STAR)

    assert node.is_safe


def test_node_equality():
    """Each node is always Unique."""
    node_1 = Node()
    node_1.id = 100
    node_2 = Node()
    node_2.id = 100

    nodes = {node_1, node_2}

    assert node_1 == node_2
    assert len(nodes) == 1


def test_add_two_tokens_in_single_node():
    """Check Add current token in a node."""
    blue_house = DummyHouse(HouseType.BLUE)

    home_node_1 = Node(NodeType.HOME, blue_house)
    home_node_2 = Node(NodeType.HOME, blue_house)
    node_3 = Node()

    token_1 = Token(home_node_1)
    token_2 = Token(home_node_2)

    node_3.add_token(token_1)
    node_3.add_token(token_2)

    assert len(node_3.tokens) == 2


def test_remove_one_token_from_single_node():
    """Check the current token remove from the node."""
    blue_house = DummyHouse(HouseType.BLUE)

    home_node_1 = Node(NodeType.HOME, blue_house)
    home_node_2 = Node(NodeType.HOME, blue_house)
    node_3 = Node()

    token_1 = Token(home_node_1)
    token_2 = Token(home_node_2)

    node_3.add_token(token_1)
    node_3.add_token(token_2)

    assert len(node_3.tokens) == 2

    node_3.remove_token(token_1)

    assert len(node_3.tokens) == 1


def test_add_only_one_token_on_home_node():
    """Check Home node has a token."""
    blue_house = DummyHouse(HouseType.BLUE)

    home_node = Node(NodeType.HOME, blue_house)

    Token(home_node)
    assert len(home_node.tokens) == 1

    with pytest.raises(Exception):
        Token(home_node)


def test_house_token_to_add_on_same_house_node():
    """Check house token add on house node."""
    blue_house = DummyHouse(HouseType.BLUE)

    house_node = Node(NodeType.HOUSE, blue_house)

    token = Token(house_node)

    house_node.add_token(token)

    assert len(house_node.tokens) == 1


def test_house_token_to_add_on_different_house_node():
    """Check house token add on different house node."""
    blue_house = DummyHouse(HouseType.BLUE)
    red_house = DummyHouse(HouseType.RED)

    house_node = Node(NodeType.HOUSE, blue_house)

    home_node = Node(NodeType.HOME, red_house)

    token = Token(home_node)

    with pytest.raises(Exception):
        house_node.add_token(token)


def test_current_tokens_node_is_fork_node():
    """Initialize Blue house's Fork Node."""
    blue_house = DummyHouse(HouseType.BLUE)
    fork_node = Node(NodeType.FORK, blue_house)

    token_1 = Token(fork_node)

    fork_node.add_token(token_1)

    assert token_1.current_node.node_type == NodeType.FORK


def test_creating_home_node_without_house_fails():
    """Handle Exception when creating home node without house fails."""
    with pytest.raises(Exception):
        Node(NodeType.HOME)


def test_creating_house_node_without_house_fails():
    """Handle Exception when creating house node without house fails."""
    with pytest.raises(Exception):
        Node(NodeType.HOUSE)


def test_creating_fork_node_without_house_fails():
    """Handle Exception when creating fork node without house fails."""
    with pytest.raises(Exception):
        Node(NodeType.FORK)


def test_end_node_has_house():
    """Each End node must always have a House."""
    blue_house = DummyHouse(HouseType.BLUE)
    end_node = Node(NodeType.END, blue_house)

    assert end_node.house


def test_end_node_does_not_have_house():
    """Handle Exception when create End node without house fails."""
    with pytest.raises(Exception):
        Node(NodeType.END)
