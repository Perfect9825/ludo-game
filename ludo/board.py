"""Board Package."""

from ludo.house import HouseType, House


class Board:
    """Represent Ludo Game Board."""

    def __init__(self):
        """
        Initialize a Board.

        When create a board object, every house nodes and tokens create and
        every node set with next node.
        """
        self.blue_house = House(HouseType.BLUE)
        self.red_house = House(HouseType.RED)
        self.green_house = House(HouseType.GREEN)
        self.yellow_house = House(HouseType.YELLOW)

        self.blue_house.set_next_house(self.red_house)
        self.red_house.set_next_house(self.green_house)
        self.green_house.set_next_house(self.yellow_house)
        self.yellow_house.set_next_house(self.blue_house)

        self.nodes = []
        self.nodes.extend(self.blue_house.nodes)
        self.nodes.extend(self.red_house.nodes)
        self.nodes.extend(self.yellow_house.nodes)
        self.nodes.extend(self.green_house.nodes)

        self.tokens = []
        self.tokens.extend(self.blue_house.tokens)
        self.tokens.extend(self.red_house.tokens)
        self.tokens.extend(self.yellow_house.tokens)
        self.tokens.extend(self.green_house.tokens)

        self.winner_house = None

    def get_node(self, node_id):
        """Get node by node id."""
        return [node for node in self.nodes if node.id == node_id][0]

    def get_token(self, token_id):
        """Get token by token id."""
        return [token for token in self.tokens if token.id == token_id][0]

    def completed(self):
        """Check any 3 houses tokens reached end then game completed."""
        num_houses_with_all_tokens_reached_end = 0
        if self.blue_house.all_tokens_reached_end():
            if not self.winner_house:
                self.winner_house = self.blue_house
            num_houses_with_all_tokens_reached_end += 1
        if self.red_house.all_tokens_reached_end():
            if not self.winner_house:
                self.winner_house = self.red_house
            num_houses_with_all_tokens_reached_end += 1
        if self.green_house.all_tokens_reached_end():
            if not self.winner_house:
                self.winner_house = self.green_house
            num_houses_with_all_tokens_reached_end += 1
        if self.yellow_house.all_tokens_reached_end():
            if not self.winner_house:
                self.winner_house = self.yellow_house
            num_houses_with_all_tokens_reached_end += 1

        return num_houses_with_all_tokens_reached_end == 3
