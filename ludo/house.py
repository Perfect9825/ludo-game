"""House Package."""

from enum import Enum

from ludo.node import Node, NodeType
from ludo.token import Token

FORK_NODE_INDEX = 0
START_NODE_INDEX = 2
STAR_NODE_INDEX = 10
LAST_NODE_INDEX = 12
FIRST_HOUSE_NODE_INDEX = 13
END_NODE_INDEX = 18


class HouseType(Enum):
    """Represent The House category."""

    BLUE = "blue"
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"


class House:
    """Represent the Ludo Game House."""

    internal_id = 1  # Class variable

    def __init__(self, type):
        """Create a House object with the given unique House id."""
        self.id = House.internal_id
        House.internal_id += 1
        # a house_type member which contains the type of house colour.
        self.type = type
        # a house_tokens member which contains the tokens of the house.
        self.tokens = set()
        # A home_nodes member which contains the Home nodes of the house.
        self.home_nodes = set()
        # Make nodes of the ludo graph.
        self.nodes = []
        # Keep a list of all 5 house nodes only
        self.house_nodes = []
        # Create each house's tokens and nodes.
        self.create_nodes_and_tokens()
        # The next house with tokens in play
        self.next_house = None

    def __hash__(self):
        """Uniquely identifiable House object."""
        return hash(self.id)

    def __eq__(self, other):
        """Uniquely identifiable House object."""
        return isinstance(other, House) and self.id == other.id

    def __str__(self):
        """Uniquely identifiable string representation of House object."""
        return f"House_Id: {self.id}\n" f"House_type: {self.type}\n"

    def __repr__(self):
        """Uniquely identifiable string representation of House object."""
        return f"House_Id: {self.id}\n" f"House_type: {self.type}\n"

    def add_token(self, token):
        """Add each House's 4 tokens in house tokens."""
        if len(self.tokens) < 4:
            self.tokens.add(token)
            return
        raise Exception(
            f"Attempt to add house token {token.id} "
            f"{token.house.type} to home node {token.house.id} "
            f"{self.type} with {len(self.tokens)} token."
        )

    def all_tokens_reached_end(self):
        """All Home's tokens reached end."""
        for token in self.tokens:
            if not token.reached_end():
                return False
        return True

    def create_nodes_and_tokens(self):
        """
        Create tokens and nodes. Set every node with next node.

        Generate 19 nodes and 4 tokens at a time for each house and all
        generated 19 nodes link with each other's next node.
        """
        # Create 4 Home nodes for each house.
        home_node_1 = Node(NodeType.HOME, self)
        self.home_nodes.add(home_node_1)
        home_node_2 = Node(NodeType.HOME, self)
        self.home_nodes.add(home_node_2)
        home_node_3 = Node(NodeType.HOME, self)
        self.home_nodes.add(home_node_3)
        home_node_4 = Node(NodeType.HOME, self)
        self.home_nodes.add(home_node_4)

        # Create 4 tokens for each house.
        Token(home_node_1)
        Token(home_node_2)
        Token(home_node_3)
        Token(home_node_4)

        # Keep a running count of nodes created.
        count_nodes = 0

        # Add Fork Node for house.
        self.nodes.append(Node(NodeType.FORK, self))
        count_nodes += 1
        # Add a Regular Node.
        self.nodes.append(Node())
        count_nodes += 1
        # Add a Start Node for house.
        self.nodes.append(Node(NodeType.START))
        count_nodes += 1

        # Set the next start node for each Home node.
        home_node_1.next_node = self.nodes[START_NODE_INDEX]
        home_node_2.next_node = self.nodes[START_NODE_INDEX]
        home_node_3.next_node = self.nodes[START_NODE_INDEX]
        home_node_4.next_node = self.nodes[START_NODE_INDEX]

        # Make 7 Regular nodes.
        num_regular_nodes_after_start_node = 7
        for i in range(num_regular_nodes_after_start_node):
            self.nodes.append(Node())
        count_nodes += num_regular_nodes_after_start_node

        # Add a Star Node.
        self.nodes.append(Node(NodeType.STAR))
        count_nodes += 1

        # Add 2 Regular nodes.
        num_regular_nodes_after_star_node = 2
        for i in range(num_regular_nodes_after_star_node):
            self.nodes.append(Node())
        count_nodes += num_regular_nodes_after_star_node

        # Set the next node for each node.
        for i in range(1, count_nodes):
            node_1 = self.nodes[i - 1]
            node_2 = self.nodes[i]
            node_1.next_node = node_2

        # Make every house's 5 House node for reach end.
        num_house_nodes = 5
        for i in range(num_house_nodes):
            house_node = Node(NodeType.HOUSE, self)
            self.nodes.append(house_node)
            self.house_nodes.append(house_node)
        house_node_start_index = count_nodes
        count_nodes += num_house_nodes

        # Add an End Node.
        self.nodes.append(Node(NodeType.END, self))
        count_nodes += 1

        # Set fork node with next house node.
        self.nodes[FORK_NODE_INDEX].next_house_node = self.nodes[
            FIRST_HOUSE_NODE_INDEX
        ]

        # Set every house's house node with the next node.
        for i in range(house_node_start_index, count_nodes):
            node_1 = self.nodes[i - 1]
            node_2 = self.nodes[i]
            node_1.next_node = node_2

    def get_fork_node(self):
        """Get current house's fork node."""
        return self.nodes[FORK_NODE_INDEX]

    def get_last_node(self):
        """Get current house's last node."""
        return self.nodes[LAST_NODE_INDEX]

    def get_start_node(self):
        """Get current house's start node."""
        return self.nodes[START_NODE_INDEX]

    def get_first_house_node(self):
        """Get current house's first house node."""
        return self.nodes[FIRST_HOUSE_NODE_INDEX]

    def get_end_node(self):
        """Get current house's end node."""
        return self.nodes[END_NODE_INDEX]

    def get_star_node(self):
        """Get current house's star node."""
        return self.nodes[STAR_NODE_INDEX]

    def set_next_house(self, next_house):
        """Pointing last node's next node to next house's fork node."""
        self.next_house = next_house
        self.get_last_node().next_node = next_house.get_fork_node()

    def get_tokens_in_house(self):
        """All Home's tokens reached end."""
        return [token.id for token in self.tokens if token.in_house]

    def get_token_ids_in_play(self):
        """Return specific token is out of house."""
        return [
            token.id
            for token in self.tokens
            if not token.in_house and not token.reached_end()
        ]

    def get_all_token_home_node_ids(self):
        """Get all token's home node ids."""
        return [token.home_node.id for token in self.tokens if token.in_house]
