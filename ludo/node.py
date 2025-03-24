"""Node Package."""

from enum import Enum


class NodeType(Enum):
    """Represent The node category."""

    HOUSE = "house"
    HOME = "home"
    REGULAR = "regular"
    START = "start"
    STAR = "star"
    END = "end"
    FORK = "fork"


class Node:
    """Represent Ludo Game Node(Step)."""

    internal_id = 0  # Class variable

    def __init__(self, node_type=NodeType.REGULAR, house=None):
        """Represent unique node id."""
        if (
            node_type == NodeType.HOME
            or node_type == NodeType.HOUSE
            or node_type == NodeType.FORK
            or node_type == NodeType.END
        ) and house is None:
            raise Exception(f"Cannot create {node_type} node without house.")
        self.id = Node.internal_id
        Node.internal_id += 1
        # Pointing Node member to next Node.
        self.next_node = None
        # Pointing Node member to which type of Node.
        self.node_type = node_type
        # Pointing Node member to safe Node.
        self.is_safe = (
            node_type != NodeType.REGULAR and node_type != NodeType.FORK
        )
        # Represents the unique tokens set.
        self.tokens = set()
        # Represents the House's node.
        self.house = house
        # Pointing Node member to House node.
        self.next_house_node = None

    def __hash__(self):
        """Uniquely identifiable Node object."""
        return hash(self.id)

    def __eq__(self, other):
        """Uniquely identifiable Node object."""
        return isinstance(other, Node) and self.id == other.id

    def __str__(self):
        """Uniquely identifiable string representation of Node object."""
        return (
            f"Node_Id: {self.id}\n Node_Type: {self.node_type}\n"
            f"Node_Safe: {self.is_safe}\n Node_House: {self.house.type}"
        )

    def __repr__(self):
        """Uniquely identifiable string representation of Node object."""
        return f"Node_Id: {self.id}\n"

    def add_token(self, token):
        """Add the unique current token."""
        if self.node_type == NodeType.HOME:
            if len(self.tokens) == 0:
                self.tokens.add(token)
                return
            raise Exception(
                f"Attempt to add token {token.id} "
                f"{token.house.type} to home node {self.id} "
                f"{self.house.type} with {len(self.tokens)} token."
            )
        elif self.node_type == NodeType.HOUSE:
            if token.house == self.house:
                self.tokens.add(token)
                return
            raise Exception(
                f"Attempt to add token {token.id} "
                f"{token.house.type} to house node {self.id} "
                f"{self.house.type}."
            )
        else:
            self.tokens.add(token)

    def remove_token(self, old_token):
        """Remove the unique old token."""
        self.tokens.remove(old_token)

    def has_n_next_nodes(self, n):
        """Check 'n' times node has next node."""
        current_node = self
        for i in range(n):
            if not current_node.next_node:
                return False
            else:
                current_node = current_node.next_node
        return True
