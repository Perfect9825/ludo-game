"""Tests for Board module."""

from ludo.board import Board
from ludo.node import NodeType


def test_board_is_valid():
    """Check all house valid."""
    board = Board()

    check_house(board.blue_house)
    check_house(board.red_house)
    check_house(board.green_house)
    check_house(board.yellow_house)


def check_house(house):
    """Check some validation for created board is valid or not."""
    house_fork_node = house.get_fork_node()
    house_start_node = house.get_start_node()
    house_first_house_node = house.get_first_house_node()
    house_end_node = house.get_end_node()
    house_star_node = house.get_star_node()
    assert len(house.tokens) == 4
    assert house_fork_node.next_node == house.nodes[1]
    assert house_fork_node.next_house_node == house_first_house_node
    assert len(house.home_nodes) == 4
    for home_node in house.home_nodes:
        assert home_node.next_node == house_start_node
    assert house_end_node.next_node is None
    assert house_star_node.is_safe
    assert house_start_node.is_safe
    for home_node in house.home_nodes:
        assert home_node.is_safe
    for node in house.nodes:
        if node.node_type != NodeType.END:
            assert node.next_node
