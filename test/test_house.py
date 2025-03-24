"""Tests for House module."""

from ludo.house import HouseType
from ludo.node import Node, NodeType
from ludo.token import Token
from test.utils import DummyHouse, create_house
import pytest


def test_each_house_has_colour():
    """Each house must always have a house colour."""
    blue_house = DummyHouse(HouseType.BLUE)

    assert blue_house.type is HouseType.BLUE


def test_house_has_token():
    """Check each House has a token."""
    blue_house = DummyHouse(HouseType.BLUE)

    blue_house_home_node = Node(NodeType.HOME, blue_house)

    Token(blue_house_home_node)

    assert len(blue_house.tokens) == 1


def test_house_does_not_have_more_than_four_tokens():
    """Handle Exception when create nore than four tokens."""
    blue_house = DummyHouse(HouseType.BLUE)

    blue_house_home_node_1 = Node(NodeType.HOME, blue_house)
    blue_house_home_node_2 = Node(NodeType.HOME, blue_house)
    blue_house_home_node_3 = Node(NodeType.HOME, blue_house)
    blue_house_home_node_4 = Node(NodeType.HOME, blue_house)
    blue_house_home_node_5 = Node(NodeType.HOME, blue_house)

    Token(blue_house_home_node_1)
    Token(blue_house_home_node_2)
    Token(blue_house_home_node_3)
    Token(blue_house_home_node_4)

    with pytest.raises(Exception):
        Token(blue_house_home_node_5)


def test_all_tokens_reached_end():
    """Check all house's tokens reached end."""
    blue_house = create_house()

    blue_house_tokens = list(blue_house.tokens)

    blue_house_end_node = Node(NodeType.END, blue_house)

    token_1 = blue_house_tokens[0]
    token_1_home_node = token_1.home_node
    token_1.in_house = False
    token_1_home_node.remove_token(token_1)
    token_1.current_node = blue_house_end_node
    blue_house_end_node.add_token(token_1)

    token_2 = blue_house_tokens[1]
    token_2_home_node = token_2.home_node
    token_2.in_house = False
    token_2_home_node.remove_token(token_2)
    token_2.current_node = blue_house_end_node
    blue_house_end_node.add_token(token_2)

    token_3 = blue_house_tokens[2]
    token_3_home_node = token_3.home_node
    token_3.in_house = False
    token_3_home_node.remove_token(token_3)
    token_3.current_node = blue_house_end_node
    blue_house_end_node.add_token(token_3)

    token_4 = blue_house_tokens[3]
    token_4_home_node = token_4.home_node
    token_4.in_house = False
    token_4_home_node.remove_token(token_4)
    token_4.current_node = blue_house_end_node
    blue_house_end_node.add_token(token_4)

    assert blue_house.all_tokens_reached_end()


def test_all_tokens_not_reached_end():
    """Check all house's tokens not reached end."""
    blue_house = DummyHouse(HouseType.BLUE)

    blue_house_home_node_1 = Node(NodeType.HOME, blue_house)
    blue_house_home_node_2 = Node(NodeType.HOME, blue_house)
    blue_house_home_node_3 = Node(NodeType.HOME, blue_house)
    blue_house_home_node_4 = Node(NodeType.HOME, blue_house)

    blue_house_end_node = Node(NodeType.END, blue_house)

    token_1 = Token(blue_house_home_node_1)
    token_1.in_house = False
    blue_house_home_node_1.remove_token(token_1)
    token_1.current_node = blue_house_end_node
    blue_house_end_node.add_token(token_1)

    Token(blue_house_home_node_2)
    Token(blue_house_home_node_3)
    Token(blue_house_home_node_4)

    assert not blue_house.all_tokens_reached_end()
