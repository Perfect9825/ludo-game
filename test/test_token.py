"""Tests for Token module."""

from ludo.token import Token
from ludo.node import Node, NodeType
from test.utils import create_nodes, create_dummy_house, create_house


def test_token_move_out_of_house():
    """Tests the move out of house for all numbers 1 to 6 rolled on the dice."""
    blue_house = create_dummy_house()

    home_node = Node(NodeType.HOME, blue_house)
    home_node.next_node = Node()

    token = Token(home_node)

    assert token is not None
    assert token.in_house
    assert token.current_node is not None

    #   token is not moved if dice rolls 1 to 5
    for i in range(1, 6):
        assert len(token.current_node.tokens) == 1
        assert token in token.current_node.tokens
        token.move(i)
        assert len(token.current_node.tokens) == 1
        assert token in token.current_node.tokens
        assert token.in_house
        assert token.current_node

    #   token is moved if dice rolls 6
    assert len(token.current_node.tokens) == 1
    assert token in token.current_node.tokens
    token.move(6)
    assert len(home_node.tokens) == 0
    assert len(token.current_node.tokens) == 1
    assert token in token.current_node.tokens
    assert not token.in_house
    assert token.current_node


def test_move_token_already_out_of_house_for_dice_roll_1():
    """
    We need a home node.

    Which points to another node which in turn points to another node.
    """
    blue_house = create_dummy_house()

    home_node = create_nodes(3, blue_house)

    token = Token(home_node)
    # To bring token out of the house.
    token.move(6)
    # Once the token out of the house then the token moves 1 step.
    assert len(token.current_node.tokens) == 1
    assert token in token.current_node.tokens
    token.move(1)
    check_previous_nodes(home_node, 2)
    assert token in token.current_node.tokens
    assert token.current_node.id == 2


def test_move_token_already_out_of_house_for_dice_roll_2():
    """
    We need a home node.

    Which points to another node which in turn points to another node.
    """
    blue_house = create_dummy_house()
    home_node = create_nodes(4, blue_house)

    token = Token(home_node)
    # To bring token out of the house.
    token.move(6)
    # Once the token out of the house then the token move 2 steps.
    assert len(token.current_node.tokens) == 1
    assert token in token.current_node.tokens
    token.move(2)
    check_previous_nodes(home_node, 3)
    assert token.current_node.id == 3


def check_previous_nodes(previous_node, num_nodes):
    """Check the current token is not in every previous node."""
    for i in range(num_nodes):
        assert len(previous_node.tokens) == 0
        previous_node = previous_node.next_node


def test_move_token_already_out_of_house_for_dice_roll_3():
    """
    We need a home node.

    Which points to another node which in turn points to another node.
    """
    blue_house = create_dummy_house()
    home_node = create_nodes(5, blue_house)

    token = Token(home_node)
    # To bring token out of the house.
    token.move(6)
    # Once the token out of the house then the token move 3 steps.
    assert len(token.current_node.tokens) == 1
    assert token in token.current_node.tokens
    token.move(3)
    check_previous_nodes(home_node, 4)
    assert token.current_node.id == 4


def test_move_token_already_out_of_house_for_dice_roll_4():
    """
    We need a home node.

    Which points to another node which in turn points to another node.
    """
    blue_house = create_dummy_house()
    home_node = create_nodes(6, blue_house)

    token = Token(home_node)
    # To bring token out of the house.
    token.move(6)
    # Once the token out of the house then the token moves 4 steps.
    assert len(token.current_node.tokens) == 1
    assert token in token.current_node.tokens
    token.move(4)
    check_previous_nodes(home_node, 5)
    assert token.current_node.id == 5


def test_move_token_already_out_of_house_for_dice_roll_5():
    """
    We need a home node.

    Which points to another node which in turn points to another node.
    """
    blue_house = create_dummy_house()
    home_node = create_nodes(7, blue_house)

    token = Token(home_node)
    # To bring token out of the house.
    token.move(6)
    # Once the token out of the house then the token moves 5 steps.
    assert len(token.current_node.tokens) == 1
    assert token in token.current_node.tokens
    token.move(5)
    check_previous_nodes(home_node, 6)
    assert token.current_node.id == 6


def test_move_token_already_out_of_house_for_dice_roll_6():
    """
    We need a home node.

    Which points to another node which in turn points to another node.
    """
    blue_house = create_dummy_house()
    home_node = create_nodes(8, blue_house)

    token = Token(home_node)
    # To bring token out of the house.
    token.move(6)
    # Once the token out of the house then the token moves 6 steps.
    assert len(token.current_node.tokens) == 1
    assert token in token.current_node.tokens
    token.move(6)
    check_previous_nodes(home_node, 7)
    assert token.current_node.id == 7


def test_token_equality():
    """Each Token is always Unique."""
    blue_house = create_dummy_house()
    home_node_1 = Node(NodeType.HOME, blue_house)
    home_node_2 = Node(NodeType.HOME, blue_house)

    token_1 = Token(home_node_1)
    token_1.id = 100
    token_2 = Token(home_node_2)
    token_2.id = 100

    tokens = {token_1, token_2}

    assert token_1 == token_2
    assert len(tokens) == 1


def test_reset_token():
    """After reset the token current node will be home node."""
    blue_house = create_dummy_house()
    home_node = create_nodes(5, blue_house)

    token_1 = Token(home_node)

    token_1.move(6)
    assert token_1.current_node.id == 1

    token_1.move(3)
    assert token_1.current_node.id == 4

    token_1.reset()
    assert token_1.current_node == home_node


def test_unsafe_node_with_no_other_tokens():
    """Kill no other tokens on unsafe node."""
    blue_house = create_dummy_house()

    home_node = Node(NodeType.HOME, blue_house)
    unsafe_node = Node()  # create an unsafe node

    moved_token = Token(home_node)
    moved_token.current_node = unsafe_node

    moved_token.kill_tokens()

    assert len(moved_token.current_node.tokens) == 0


def test_unsafe_node_with_other_tokens_of_same_house():
    """Kill other tokens on unsafe node of same house."""
    blue_house = create_dummy_house()

    home_node_1 = Node(NodeType.HOME, blue_house)
    home_node_2 = Node(NodeType.HOME, blue_house)
    unsafe_node = Node()

    token_1 = Token(home_node_1)
    token_1.current_node = unsafe_node
    unsafe_node.add_token(token_1)

    moved_token = Token(home_node_2)
    moved_token.current_node = unsafe_node

    moved_token.kill_tokens()

    assert len(moved_token.current_node.tokens) == 1


def test_unsafe_node_with_other_tokens_of_other_houses_only():
    """Kill other tokens on unsafe node of other houses only."""
    blue_house = create_dummy_house()
    red_house = blue_house.next_house

    blue_house_home_node_1 = Node(NodeType.HOME, blue_house)
    blue_house_home_node_2 = Node(NodeType.HOME, blue_house)
    red_house_home_node = Node(NodeType.HOME, red_house)
    unsafe_node = Node()

    token_1 = Token(blue_house_home_node_1)
    blue_house_home_node_1.remove_token(token_1)
    token_1.current_node = unsafe_node
    unsafe_node.add_token(token_1)

    token_2 = Token(blue_house_home_node_2)
    blue_house_home_node_2.remove_token(token_2)
    token_2.current_node = unsafe_node
    unsafe_node.add_token(token_2)

    moved_token = Token(red_house_home_node)
    moved_token.current_node = unsafe_node

    moved_token.kill_tokens()

    assert len(moved_token.current_node.tokens) == 0


def test_safe_node_with_no_other_tokens():
    """Not Kill no other tokens on safe node."""
    blue_house = create_dummy_house()

    home_node = Node(NodeType.HOME, blue_house)
    safe_node = Node(NodeType.START)

    moved_token = Token(home_node)
    moved_token.current_node = safe_node

    moved_token.kill_tokens()

    assert len(moved_token.current_node.tokens) == 0


def test_safe_node_with_other_tokens_of_same_house():
    """Not Kill other tokens on safe node of same house."""
    blue_house = create_dummy_house()

    home_node_1 = Node(NodeType.HOME, blue_house)
    home_node_2 = Node(NodeType.HOME, blue_house)
    safe_node = Node(NodeType.START)

    token_1 = Token(home_node_1)
    token_1.current_node = safe_node
    safe_node.add_token(token_1)

    moved_token = Token(home_node_2)
    moved_token.current_node = safe_node

    moved_token.kill_tokens()

    assert len(moved_token.current_node.tokens) == 1


def test_safe_node_with_other_tokens_of_other_houses_only():
    """Not Kill other tokens of other houses only on safe node."""
    blue_house = create_dummy_house()
    red_house = blue_house.next_house

    blue_house_home_node_1 = Node(NodeType.HOME, blue_house)
    blue_house_home_node_2 = Node(NodeType.HOME, blue_house)
    red_house_home_node = Node(NodeType.HOME, red_house)
    safe_node = Node(NodeType.START)

    token_1 = Token(blue_house_home_node_1)
    token_1.current_node = safe_node
    safe_node.add_token(token_1)

    token_2 = Token(blue_house_home_node_2)
    token_2.current_node = safe_node
    safe_node.add_token(token_2)

    moved_token = Token(red_house_home_node)
    moved_token.current_node = safe_node

    moved_token.kill_tokens()

    assert len(moved_token.current_node.tokens) == 2


def test_safe_node_with_other_tokens_of_same_and_other_houses():
    """Not Kill other tokens of same and other houses on safe node."""
    blue_house = create_dummy_house()
    red_house = blue_house.next_house

    blue_house_home_node_1 = Node(NodeType.HOME, blue_house)
    blue_house_home_node_2 = Node(NodeType.HOME, blue_house)
    red_house_home_node_1 = Node(NodeType.HOME, red_house)
    red_house_home_node_2 = Node(NodeType.HOME, red_house)
    star_safe_node = Node(NodeType.STAR)

    token_1 = Token(blue_house_home_node_1)
    blue_house_home_node_1.remove_token(token_1)
    token_1.current_node = star_safe_node
    star_safe_node.add_token(token_1)

    token_2 = Token(blue_house_home_node_2)
    blue_house_home_node_2.remove_token(token_2)
    token_2.current_node = star_safe_node
    star_safe_node.add_token(token_2)

    token_3 = Token(red_house_home_node_1)
    red_house_home_node_1.remove_token(token_3)
    token_3.current_node = star_safe_node
    star_safe_node.add_token(token_3)

    moved_token = Token(red_house_home_node_2)
    moved_token.current_node = star_safe_node

    moved_token.kill_tokens()

    assert len(moved_token.current_node.tokens) == 3


def test_token_reached_end():
    """Current token reached end node."""
    blue_house = create_dummy_house()

    home_node = Node(NodeType.HOME, blue_house)
    end_node = Node(NodeType.END, blue_house)

    token = Token(home_node)
    token.current_node = end_node

    assert token.reached_end()


def test_token_not_reached_end():
    """Current token not reached end node."""
    blue_house = create_dummy_house()

    home_node = Node(NodeType.HOME, blue_house)
    regular_node = Node()

    token = Token(home_node)
    token.current_node = regular_node

    assert not token.reached_end()


def test_same_house_token_on_fork_node():
    """
    Check a Fork node belongs to a certain House.

    The node when moving is a fork_node and turn right if the token being moved
    belongs to the same house as the fork node.
    """
    blue_house = create_dummy_house()

    home_node = Node(NodeType.HOME, blue_house)
    fork_node = Node(NodeType.FORK, blue_house)
    blue_house_node = Node(NodeType.HOUSE, blue_house)
    fork_next_node = Node()

    fork_node.next_house_node = blue_house_node
    fork_node.next_node = fork_next_node

    token_1 = Token(home_node)
    token_1.in_house = False

    token_1.current_node = fork_node
    fork_node.add_token(token_1)

    token_1.move(1)

    assert len(fork_node.tokens) == 0
    assert len(token_1.current_node.tokens) == 1


def test_different_house_token_on_fork_node():
    """
    Check a Fork node not belongs to a certain House.

    The node when moving is a fork_node and turn left if the token is not being
    moved belongs to the same house as the fork node.
    """
    blue_house = create_dummy_house()
    red_house = blue_house.next_house

    red_house_home_node = Node(NodeType.HOME, red_house)
    blue_house_fork_node = Node(NodeType.FORK, blue_house)
    blue_house_next_house_node = Node(NodeType.HOUSE, blue_house)
    blue_house_fork_next_node = Node()

    blue_house_fork_node.next_house_node = blue_house_next_house_node
    blue_house_fork_node.next_node = blue_house_fork_next_node

    token_1 = Token(red_house_home_node)
    token_1.in_house = False

    token_1.current_node = blue_house_fork_node
    blue_house_fork_node.add_token(token_1)

    token_1.move(1)

    assert len(blue_house_fork_node.tokens) == 0
    assert len(token_1.current_node.tokens) == 1
    assert token_1.current_node.node_type == NodeType.REGULAR


def test_same_house_token_reaches_end_node():
    """
    Check a Fork node belongs to a certain House.

    A fork node belongs to a certain House and allows tokens of that House to
    reach the end node.
    """
    blue_house = create_house()

    blue_house_tokens = list(blue_house.tokens)

    blue_house_fork_node = blue_house.get_fork_node()

    token_1 = blue_house_tokens[0]
    token_1.in_house = False

    token_1.current_node = blue_house_fork_node
    blue_house_fork_node.add_token(token_1)

    token_1.move(6)

    assert len(blue_house_fork_node.tokens) == 0
    check_previous_nodes(blue_house_fork_node.next_house_node, 5)
    assert token_1.reached_end()
    assert len(token_1.current_node.tokens) == 1
    assert token_1.current_node.node_type == NodeType.END
