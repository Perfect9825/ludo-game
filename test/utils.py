"""Create this utils for testing purpose."""

from ludo.house import House, HouseType
from ludo.node import Node, NodeType


class DummyHouse(House):
    """This is for Testing purpose."""

    def __init__(self, type):
        """Create dummy house instance."""
        super().__init__(type)

    def create_nodes_and_tokens(self):
        """For testing we don't need actual nodes and tokens."""
        pass

    def all_tokens_reached_end(self):
        """As this is a dummy house, and we have no tokens, we return False."""
        return False


def create_nodes(num_nodes, home_node_house):
    """Create nodes with no of nodes input."""
    Node.internal_id = 0
    nodes = [Node(NodeType.HOME, home_node_house)]

    for i in range(num_nodes - 1):
        nodes.append(Node())

    # Set the next node for each node.
    for i in range(1, num_nodes):
        node_1 = nodes[i - 1]
        node_2 = nodes[i]
        node_1.next_node = node_2

    return nodes[0]  # Return all nodes from linked nodes.


def create_dummy_house():
    """Create dummy houses for testing purpose."""
    blue_house = DummyHouse(HouseType.BLUE)
    red_house = DummyHouse(HouseType.RED)
    green_house = DummyHouse(HouseType.GREEN)
    yellow_house = DummyHouse(HouseType.YELLOW)
    blue_house.next_house = red_house
    red_house.next_house = green_house
    green_house.next_house = yellow_house
    yellow_house.next_house = blue_house
    return blue_house


def create_house():
    """Create houses for testing purpose."""
    blue_house = House(HouseType.BLUE)
    red_house = House(HouseType.RED)
    green_house = House(HouseType.GREEN)
    yellow_house = House(HouseType.YELLOW)
    blue_house.next_house = red_house
    red_house.next_house = green_house
    green_house.next_house = yellow_house
    yellow_house.next_house = blue_house
    return blue_house
