"""Token Package."""

from ludo.node import NodeType


class Token:
    """Represent Ludo Game Token(Player's Coin)."""

    internal_id = 1  # Class variable

    def __init__(self, home_node):
        """
        Create a token object with the given start node.

        The current node represents the current position of the token on the
        board.
        The in_house flag indicates the token is in house before dice roll 6.
        """
        self.id = Token.internal_id  # Represent unique token id.
        Token.internal_id += 1
        # Store Home node for future uses.
        self.home_node = home_node
        self.current_node = home_node
        self.in_house = True
        # House member which represents the House instance.
        self.house = home_node.house
        # Add token on the current node.
        self.current_node.add_token(self)
        # Add token in House.
        self.house.add_token(self)
        # If it killed tokens of other house during a move
        self.killed_other_tokens = False
        self.killed_other_token_ids = []

    def __hash__(self):
        """Uniquely identifiable Token object."""
        return hash(self.id) + hash(self.house.id) * 11

    def __eq__(self, other):
        """Uniquely identifiable Token object."""
        return (
            isinstance(other, self.__class__)
            and self.id == other.id
            and self.house.id == other.house.id
        )

    def __str__(self):
        """Uniquely identifiable string representation of Token object."""
        return (
            f"Token_Id: {self.id}\n"
            f"Current_Node_id: {self.current_node.id}\n"
            f"House_Colour: {self.house.type}\n"
        )

    def __repr__(self):
        """Uniquely identifiable string representation of Token object."""
        return (
            f"Token_Id: {self.id}\n"
            f"Current_Node_id: {self.current_node.id}\n"
            f"House_Colour: {self.house.type}\n"
        )

    def move(self, n):
        """
        Move the token.

        The token moves out of the house if the dice roll was 6 and token is in
        the house, otherwise the token moves n numbers of the nodes.
        """
        self.killed_other_tokens = False
        self.killed_other_token_ids = []
        if self.in_house:
            if n == 6:
                self.in_house = False
                self.current_node.remove_token(self)
                self.current_node = self.current_node.next_node
                self.current_node.add_token(self)
        else:
            if (
                self.is_current_node_house_node()
                and not self.current_node.has_n_next_nodes(n)
            ):
                self.set_next_house()
                return
            self.current_node.remove_token(self)
            for i in range(n):
                if (
                    self.current_node.node_type == NodeType.FORK
                    and self.current_node.house == self.house
                ):
                    self.current_node = self.current_node.next_house_node
                else:
                    self.current_node = self.current_node.next_node
            self.kill_tokens()
            self.current_node.add_token(self)
            if not self.killed_other_tokens:
                self.set_next_house()

    def reset(self):
        """Update current node position to the start node position."""
        self.in_house = True
        self.current_node.remove_token(self)
        self.current_node = self.home_node
        self.current_node.add_token(self)

    def kill_tokens(self):
        """Kill the tokens of other houses."""
        if not self.current_node.is_safe:
            other_tokens = []
            for token in self.current_node.tokens:
                if self.house != token.house:
                    other_tokens.append(token)

            for token in other_tokens:
                token.reset()

            self.killed_other_token_ids.extend(
                [token.id for token in other_tokens]
            )
            self.killed_other_tokens = len(other_tokens) > 0

    def reached_end(self):
        """Token reached end node."""
        return (
            self.current_node.node_type == NodeType.END
            and self.current_node.house.type == self.house.type
        )

    def set_next_house(self):
        """Set Next house."""
        next_house = self.house.next_house
        while next_house.all_tokens_reached_end():
            next_house = next_house.next_house
        if next_house != self.house:
            self.house.next_house = next_house

    def is_current_node_house_node(self):
        """Check current node is Home node."""
        return (
            self.current_node.node_type == NodeType.HOUSE
            and self.current_node.house == self.house
        )
