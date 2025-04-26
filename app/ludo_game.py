"""Simple version of 5x5, developed for/with Textual."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, cast
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Footer, Label

from ludo.board import Board

from random import randint

if TYPE_CHECKING:
    from typing_extensions import Final

WHITE = "#FFFFFF"
GREEN = "#009900"
GREEN_HOUSE_BG = "#9FE2BF"
RED = "#FF0000"
RED_HOUSE_BG = "#FA8072"
BLUE = "#66CCFF"
BLUE_HOUSE_BG = "#E0FFFF"
YELLOW = "#FFCC00"
YELLOW_HOUSE_BG = "#FFFACD"
HOUSE_BORDER = "#778899"
GRID_BORDER = "#FFFAFA"


class GameMessage(Label):
    """Widget to tell the user they have won."""

    MIN_MOVES: Final = 14
    """int: The minimum number of moves you can solve the puzzle in."""

    @staticmethod
    def _plural(value: int) -> str:
        return "" if value == 1 else "s"

    def show(self, msg: str) -> None:
        """Show the winner message.

        Args:
            moves (int): The number of moves required to win.
        """
        self.update(f" {msg} \n\n\n")

        self.add_class("visible")

    def hide(self) -> None:
        """Hide the winner message."""
        self.remove_class("visible")


class GameHeader(Widget):
    """Header for the game.

    Comprises the title (``#app-title``), the number of moves ``#moves``
    and the count of how many cells are turned on (``#progress``).
    """

    def compose(self) -> ComposeResult:
        """Compose the game header.

        Returns:
            ComposeResult: The result of composing the game header.
        """
        with Horizontal():
            yield Label(self.app.title, id="app-title")
            yield Label("    ")
            yield Label(id="winner_house")
            yield Label("    ")
            yield Label(id="current_house")
            yield Label(id="dice_roll")
            yield Label("            ")
            yield Label(id="header_msg")


class GameCell(Button):
    """Individual playable cell in the game."""

    @staticmethod
    def at(node_id: int) -> str:
        """Get the ID of the cell at the given location.

        Args:
            node_id (int): The node id of the cell.

        Returns:
            str: A string ID for the cell.
        """
        return f"cell-{node_id} "

    def __init__(self) -> None:
        """Initialise the game cell."""
        super().__init__(" ")
        self.node_id = None
        self.token_ids = {}


class TokenLocationCell(Button):
    """Individual playable cell in the game."""

    @staticmethod
    def at(token_id: int) -> str:
        """Get the ID of the cell at the given location.

        Args:
            token_id (int): The node id of the cell.

        Returns:
            str: A string ID for the cell.
        """
        return f"token-loc-cell-{token_id}"

    def __init__(self) -> None:
        """Initialise the game cell."""
        super().__init__("")
        self.token_id = None


class GameGrid(Widget):
    """The main playable grid of game cells."""

    def compose(self) -> ComposeResult:
        """Compose the game grid.

        Returns:
            ComposeResult: The result of composing the game grid.
        """
        self.game_cells = []
        self.board = Game.BOARD
        for _, row in enumerate(range(Game.NUM_GRID_CELLS)):
            game_cell = GameCell()
            self.game_cells.append(game_cell)
            yield game_cell

    def setup_cells(
            self,
            start_node_index,
            start_house,
            fork_node_index,
            fork_house,
            star_node_index,
            star_house,
            house_indices,
            primary_house,
            primary_house_regular_indices,
            secondary_house,
            secondary_house_regular_indices,
            main_house_bg,
            star_node_bg,
    ):
        """
        Primary and Secondary house provide nodes.

        Primary house is one which provides 12 nodes including house nodes
        and start node.
        Secondary house is one which provides 6 nodes including star node.
        """
        for game_cell_index, game_cell in enumerate(self.game_cells):
            if game_cell_index == start_node_index:
                game_cell.styles.background = main_house_bg
                game_cell.node_id = start_house.get_start_node().id
            elif game_cell_index in house_indices:
                game_cell.styles.background = main_house_bg
                house_index = house_indices.index(game_cell_index)
                game_cell.node_id = primary_house.house_nodes[house_index].id
            elif game_cell_index == fork_node_index:
                game_cell.styles.background = WHITE
                game_cell.node_id = fork_house.get_fork_node().id
            elif game_cell_index == star_node_index:
                game_cell.styles.background = star_node_bg
                game_cell.node_id = star_house.get_star_node().id
            elif game_cell_index in primary_house_regular_indices:
                game_cell.styles.background = WHITE
                node_index = primary_house_regular_indices[game_cell_index]
                game_cell.node_id = primary_house.nodes[node_index].id
            else:
                game_cell.styles.background = WHITE
                node_index = secondary_house_regular_indices[game_cell_index]
                game_cell.node_id = secondary_house.nodes[node_index].id
            game_cell.id = GameCell.at(game_cell.node_id)
            game_cell.label = f"{game_cell.node_id}"
            game_cell.styles.border = ("heavy", "black")


class GreenVerticalGameGrid(GameGrid):
    """
    Initialise style to Green Vertical game grid.

    -----------------------------------------
    |   RED HOUSE |  GRID    | GREEN HOUSE |
    -----------------------------------------
    This grid is rendered at the top. To it's right is Green house which is the
    primary house to set up 12 nodes.
    And Red house is secondary house to set up the 6 nodes.

    See super().setup_cells() for further definition of primary and secondary
    house.

    """

    def on_mount(self):
        """Initialize style to game cells."""
        self.styles.background = WHITE
        self.styles.border = ("thick", GRID_BORDER)
        start_node_index = 5
        fork_node_index = 1
        star_node_index = 6
        house_indices = [4, 7, 10, 13, 16]
        primary_house = self.board.green_house
        primary_house_regular_indices = {2: 1, 8: 3, 11: 4, 14: 5, 17: 6}
        secondary_house = self.board.red_house
        secondary_house_regular_indices = {0: 12, 3: 11, 9: 9, 12: 8, 15: 7}
        self.setup_cells(
            start_node_index,
            primary_house,
            fork_node_index,
            primary_house,
            star_node_index,
            secondary_house,
            house_indices,
            primary_house,
            primary_house_regular_indices,
            secondary_house,
            secondary_house_regular_indices,
            GREEN,
            RED,
        )


class BlueVerticalGameGrid(GameGrid):
    """
    Initialise style to Blue Vertical game grid.

    -----------------------------------------
    |   BLUE HOUSE |  GRID    | YELLOW HOUSE |
    -----------------------------------------
    This grid is rendered at the top. To it's left is Blue house which is the
    primary house to set up 12 nodes.
    And Yellow house is secondary house to set up the 6 nodes.

    See super().setup_cells() for further definition of primary and secondary
    house.

    """

    def on_mount(self):
        """Initialize style to game cells."""
        self.styles.background = WHITE
        self.styles.border = ("thick", GRID_BORDER)
        start_node_index = 12
        fork_node_index = 16
        star_node_index = 11
        house_indices = [13, 10, 7, 4, 1]
        primary_house = self.board.blue_house
        primary_house_regular_indices = {0: 6, 3: 5, 6: 4, 9: 3, 15: 1}
        secondary_house = self.board.yellow_house
        secondary_house_regular_indices = {2: 7, 5: 8, 8: 9, 14: 11, 17: 12}
        self.setup_cells(
            start_node_index,
            primary_house,
            fork_node_index,
            primary_house,
            star_node_index,
            secondary_house,
            house_indices,
            primary_house,
            primary_house_regular_indices,
            secondary_house,
            secondary_house_regular_indices,
            BLUE,
            YELLOW,
        )


class RedHorizontalGameGrid(GameGrid):
    """Initialise style to Red Horizontal game grid."""

    def on_mount(self):
        """Initialize style to game cells."""
        self.styles.background = WHITE
        self.styles.border = ("thick", GRID_BORDER)
        start_node_index = 1
        fork_node_index = 6
        star_node_index = 14
        house_indices = [7, 8, 9, 10, 11]
        primary_house = self.board.red_house
        primary_house_regular_indices = {0: 1, 2: 3, 3: 4, 4: 5, 5: 6}
        secondary_house = self.board.blue_house
        secondary_house_regular_indices = {12: 12, 13: 11, 15: 9, 16: 8, 17: 7}
        self.setup_cells(
            start_node_index,
            primary_house,
            fork_node_index,
            primary_house,
            star_node_index,
            secondary_house,
            house_indices,
            primary_house,
            primary_house_regular_indices,
            secondary_house,
            secondary_house_regular_indices,
            RED,
            BLUE,
        )


class YellowHorizontalGameGrid(GameGrid):
    """Initialise style to Yellow Horizontal game grid."""

    def on_mount(self):
        """Initialize style to game cells."""
        self.styles.background = WHITE
        self.styles.border = ("thick", GRID_BORDER)
        start_node_index = 16
        fork_node_index = 11
        star_node_index = 3
        house_indices = [10, 9, 8, 7, 6]
        primary_house = self.board.yellow_house
        primary_house_regular_indices = {12: 6, 13: 5, 14: 4, 15: 3, 17: 1}
        secondary_house = self.board.green_house
        secondary_house_regular_indices = {0: 7, 1: 8, 2: 9, 4: 11, 5: 12}
        self.setup_cells(
            start_node_index,
            primary_house,
            fork_node_index,
            primary_house,
            star_node_index,
            secondary_house,
            house_indices,
            primary_house,
            primary_house_regular_indices,
            secondary_house,
            secondary_house_regular_indices,
            YELLOW,
            GREEN,
        )


class HouseGrid(Widget):
    """The main playable grid of game cells."""

    def compose(self) -> ComposeResult:
        """Compose the game grid.

        Returns:
            ComposeResult: The result of composing the game grid.
        """
        self.tokens = []
        self.token_locations = []
        self.board = Game.BOARD
        for row in range(Game.NUM_TOKENS):
            token_cell = GameCell()
            token_loc_cell = TokenLocationCell()
            self.tokens.append(token_cell)
            self.token_locations.append(token_loc_cell)
            with Vertical():
                yield token_cell
                yield token_loc_cell


class RedHouseGrid(HouseGrid):
    """Initialise style to Red House grid."""

    def on_mount(self):
        """Initialize style to Red House tokens."""
        self.styles.background = RED_HOUSE_BG
        self.styles.border = ("thick", HOUSE_BORDER)
        self.red_house = self.board.red_house
        red_tokens = list(self.red_house.tokens)
        for index, token in enumerate(self.tokens):
            token.styles.background = RED
            red_token = red_tokens[index]
            token.node_id = red_token.home_node.id
            token_label = f"R{index + 1}-{token.node_id}"
            token.label = token_label
            token.id = GameCell.at(token.node_id)
            token.token_ids[red_token.id] = token_label

            token_loc = self.token_locations[index]
            token_loc.token_id = red_token.id
            token_loc.id = TokenLocationCell.at(token_loc.token_id)


class GreenHouseGrid(HouseGrid):
    """Initialise style to Green House grid."""

    def on_mount(self):
        """Initialize style to Green House tokens."""
        self.styles.background = GREEN_HOUSE_BG
        self.styles.border = ("thick", HOUSE_BORDER)
        self.green_house = self.board.green_house
        green_tokens = list(self.green_house.tokens)
        for index, token in enumerate(self.tokens):
            token.styles.background = GREEN
            green_token = green_tokens[index]
            token.node_id = green_token.home_node.id
            token_label = f"G{index + 1}-{token.node_id}"
            token.label = token_label
            token.id = GameCell.at(token.node_id)
            token.token_ids[green_token.id] = token_label

            token_loc = self.token_locations[index]
            token_loc.token_id = green_token.id
            token_loc.id = TokenLocationCell.at(token_loc.token_id)


class YellowHouseGrid(HouseGrid):
    """Initialise style to Yellow House grid."""

    def on_mount(self):
        """Initialize style to Yellow House tokens."""
        self.styles.background = YELLOW_HOUSE_BG
        self.styles.border = ("thick", HOUSE_BORDER)
        self.yellow_house = self.board.yellow_house
        yellow_tokens = list(self.yellow_house.tokens)
        for index, token in enumerate(self.tokens):
            token.styles.background = YELLOW
            yellow_token = yellow_tokens[index]
            token.node_id = yellow_token.home_node.id
            token_label = f"Y{index + 1}-{token.node_id}"
            token.label = token_label
            token.id = GameCell.at(token.node_id)
            token.token_ids[yellow_token.id] = token_label

            token_loc = self.token_locations[index]
            token_loc.token_id = yellow_token.id
            token_loc.id = TokenLocationCell.at(token_loc.token_id)


class BlueHouseGrid(HouseGrid):
    """Initialise style to Blue House grid."""

    def on_mount(self):
        """Initialize style to Blue House tokens."""
        self.styles.background = BLUE_HOUSE_BG
        self.styles.border = ("thick", HOUSE_BORDER)
        self.blue_house = self.board.blue_house
        blue_tokens = list(self.blue_house.tokens)
        for index, token in enumerate(self.tokens):
            token.styles.background = BLUE
            blue_token = blue_tokens[index]
            token.node_id = blue_token.home_node.id
            token_label = f"B{index + 1}-{token.node_id}"
            token.label = token_label
            token.id = GameCell.at(token.node_id)
            token.token_ids[blue_token.id] = token_label

            token_loc = self.token_locations[index]
            token_loc.token_id = blue_token.id
            token_loc.id = TokenLocationCell.at(token_loc.token_id)


class EndGrid(Widget):
    """The main playable grid of game cells."""

    def compose(self) -> ComposeResult:
        """Compose the game grid.

        Returns:
            ComposeResult: The result of composing the game grid.
        """
        self.end_cells = []
        indices = [1, 3, 5, 7]
        for i, row in enumerate(range(Game.END_GRID_CELLS)):
            if i in indices:
                label = GameCell()
            else:
                label = Label()
            self.end_cells.append(label)
            yield label

    def on_mount(self):
        """Initialize style to End grid."""
        board = Game.BOARD
        for index, end_cell in enumerate(self.end_cells):
            end_cell.label = "End"
            if index == 1:
                end_cell.styles.background = GREEN
                end_cell.node_id = board.green_house.get_end_node().id
                end_cell.id = GameCell.at(end_cell.node_id)
            elif index == 3:
                end_cell.styles.background = RED
                end_cell.node_id = board.red_house.get_end_node().id
                end_cell.id = GameCell.at(end_cell.node_id)
            elif index == 5:
                end_cell.styles.background = YELLOW
                end_cell.node_id = board.yellow_house.get_end_node().id
                end_cell.id = GameCell.at(end_cell.node_id)
            elif index == 7:
                end_cell.styles.background = BLUE
                end_cell.node_id = board.blue_house.get_end_node().id
                end_cell.id = GameCell.at(end_cell.node_id)


class Game(Screen):
    """Main 5x5 game grid screen."""

    NUM_GRID_CELLS: Final = 18
    NUM_TOKENS: Final = 4
    END_GRID_CELLS: Final = 9
    BOARD = Board()
    CURRENT_HOUSE = BOARD.red_house
    DICE_ROLL = 0
    BINDINGS = [
        Binding("r", "run_game", "Run Game"),
        Binding("n", "next_move", "Next Move"),
        Binding("q", "quit", "Quit"),
    ]
    PREV_TOKEN_LOC_CELL = None
    PREV_TOKEN_LOC_CELL_VARIANT = None

    """The bindings for the main game grid."""

    def cell(self, node_id: int) -> GameCell:
        """Get the cell at a given location.

        Args:
            node_id (int): The node id of the cell to get.

        Returns:
            GameCell: The cell at that location.
        """
        return self.query_one(f"#{GameCell.at(node_id)}", GameCell)

    def token_loc_cell(self, token_id: int) -> TokenLocationCell:
        """Get the cell at a given location.

        Args:
            token_id (int): The node id of the cell to get.

        Returns:
            GameCell: The cell at that location.
        """
        return self.query_one(
            f"#{TokenLocationCell.at(token_id)}", TokenLocationCell
        )

    def compose(self) -> ComposeResult:
        """Compose the game screen.

        Returns:
            ComposeResult: The result of composing the game screen.
        """
        yield GameHeader()
        with Horizontal():
            yield RedHouseGrid()
            yield GreenVerticalGameGrid()
            yield GreenHouseGrid()
        with Horizontal():
            yield RedHorizontalGameGrid()
            yield EndGrid()
            yield YellowHorizontalGameGrid()
        with Horizontal():
            yield BlueHouseGrid()
            yield BlueVerticalGameGrid()
            yield YellowHouseGrid()
        yield Footer()
        yield GameMessage()

    def game_cell_button_pressed(self, game_cell: GameCell) -> None:
        """Play game when pressed the game cell."""
        if Game.PREV_TOKEN_LOC_CELL:
            Game.PREV_TOKEN_LOC_CELL.variant = Game.PREV_TOKEN_LOC_CELL_VARIANT

        game_cell_msg = f"DICE ROLL: {Game.DICE_ROLL} "
        game_cell_msg += f"Pressed {game_cell.node_id} "
        if len(game_cell.token_ids) > 0:
            game_cell_msg += f"[BEFORE]: with token ids {game_cell.token_ids}\n"
            board = Game.BOARD
            token_ids = list(game_cell.token_ids.keys())
            token_choice = randint(0, len(game_cell.token_ids) - 1)
            game_cell_msg += (
                f"[BEFORE]: selected token choice {token_choice}  \n"
            )
            token_id = token_ids[token_choice]
            game_cell_msg += f"[BEFORE]: selected token id {token_id}  \n"
            token_label = game_cell.token_ids[token_id]
            token = board.get_token(token_id)
            token.move(Game.DICE_ROLL)

            del game_cell.token_ids[token_id]

            next_cell_id = token.current_node.id
            next_game_cell = self.cell(next_cell_id)
            next_game_cell.token_ids[token_id] = token_label
            # next_game_cell.styles.background = "orange"

            token_loc_cell = self.token_loc_cell(token_id)
            if token.reached_end():
                token_loc_cell.variant = "success"
                token_loc_cell.label = "REACHED END"
                Game.PREV_TOKEN_LOC_CELL = None
            else:
                for killed_token_id in token.killed_other_token_ids:
                    killed_token = board.get_token(killed_token_id)
                    killed_token_cell = self.token_loc_cell(killed_token_id)
                    killed_token_cell_id = killed_token.current_node.id
                    killed_token_home_cell = self.cell(killed_token_cell_id)
                    killed_token_home_cell.token_ids[
                        killed_token_id
                    ] = next_game_cell.token_ids[killed_token_id]
                    killed_token_cell.variant = "error"
                    killed_token_cell.label = f"At: {killed_token_cell_id}"

                    del next_game_cell.token_ids[killed_token_id]
                    Game.PREV_TOKEN_LOC_CELL = None
                token_loc_cell.variant = "warning"
                token_loc_cell.label = f"At: {next_cell_id}"
                Game.PREV_TOKEN_LOC_CELL = token_loc_cell
                Game.PREV_TOKEN_LOC_CELL_VARIANT = "primary"

            game_cell_msg += f"[AFTER] with token ids {game_cell.token_ids}\n"
            game_cell_msg += f"Next node is {next_cell_id} \n"
            game_cell_msg += (
                f"[AFTER] with token ids {next_game_cell.token_ids}"
            )
            game_cell_msg += (
                f"[AFTER] Token loc cell is {token_loc_cell.token_id} \n"
            )
        else:
            game_cell_msg += "with no tokens"

        # self.query_one(GameMessage).show(game_cell_msg)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """React to a press of a button on the game grid.

        Args:
            event (GameCell.Pressed): The event to react to.
        """
        game_cell = cast(GameCell, event.button)

        if isinstance(game_cell, TokenLocationCell):
            return
        elif isinstance(game_cell, GameCell):
            self.game_cell_button_pressed(game_cell)

    def action_new_game(self) -> None:
        """Start a new game."""
        self.query_one("#header_msg", Label).update(
            "DEMO GAME. AUTOPLAY ONLY. PRESS R NOW!!!"
        )

    def run_game_loop(self) -> None:
        """Run the game loop in a non-blocking thread."""
        self.query_one("#header_msg", Label).update("AUTO PLAYING NOW.")
        board = Game.BOARD
        while not board.completed():
            self.play_next_move()
            self.refresh()
            time.sleep(0.33)

        game_over_msg = (
            "GAME OVER. THANK YOU. QUIT, RESTART TO PLAY ANOTHER GAME!!!"
        )
        self.query_one("#winner_house", Label).update(
            f"Winner: {
            "Blue" if board.winner_house.type == board.blue_house.type else "Red"
            if board.winner_house.type == board.red_house else "Yellow"
            if board.winner_house.type == board.yellow_house else "Green"
            }"
        )
        self.query_one("#current_house", Label).update()
        self.query_one("#dice_roll", Label).update()
        self.query_one("#header_msg", Label).update(game_over_msg)

    def action_run_game(self) -> None:
        """Run the current game in autoplay mode."""
        self.game_loop_task = asyncio.create_task(
            asyncio.to_thread(self.run_game_loop)
        )

    def action_next_move(self) -> None:
        """Play next move action."""
        board = Game.BOARD
        if board.completed():
            game_over_msg = (
                "GAME OVER. THANK YOU. QUIT, RESTART TO PLAY ANOTHER GAME!!!"
            )
            self.query_one("#winner_house", Label).update(
                f"Winner: {
                "Blue" if board.winner_house.type == board.blue_house.type else "Red"
                if board.winner_house.type == board.red_house else "Yellow"
                if board.winner_house.type == board.yellow_house else "Green"
                }"
            )
            self.query_one("#current_house", Label).update()
            self.query_one("#dice_roll", Label).update()
            self.query_one("#header_msg", Label).update(game_over_msg)
        else:
            self.play_next_move()

    def play_next_move(self):
        """Play next move happened then update token, game cell and label."""
        current_house = Game.CURRENT_HOUSE
        board = Game.BOARD
        self.query_one("#current_house", Label).update(
            f"Current house: { "Blue"
            if current_house.type == board.blue_house.type else "Red"
            if current_house.type == board.red_house.type else "Yellow"
            if current_house.type == board.yellow_house.type else "Green"
            }"
        )
        Game.DICE_ROLL = randint(0, 5) + 1
        self.query_one("#dice_roll", Label).update(
            f"    Dice Roll: {Game.DICE_ROLL}"
        )
        tokens_in_house = current_house.get_tokens_in_house()
        num_tokens_in_house = len(tokens_in_house)
        killed_other_tokens = False
        play_new_token = False
        if Game.DICE_ROLL == 6:
            if num_tokens_in_house == 4:
                play_new_token = True
            elif num_tokens_in_house > 0:
                play_new_token = randint(0, 5) % 2 == 0
        if play_new_token:
            token_choice = randint(0, num_tokens_in_house - 1)
            token_home_node_ids = current_house.get_all_token_home_node_ids()
            if len(token_home_node_ids) > 0:
                home_node_id = token_home_node_ids[token_choice]
                game_cell = self.cell(home_node_id)
                self.game_cell_button_pressed(game_cell)
                self.query_one("#header_msg", Label).update(" ")
        else:
            tokens_in_play = current_house.get_token_ids_in_play()
            num_tokens_in_play = len(tokens_in_play)
            if num_tokens_in_play > 0:
                token_choice = randint(0, num_tokens_in_play - 1)
                token_id = tokens_in_play[token_choice]
                token = board.get_token(token_id)
                game_cell = self.cell(token.current_node.id)
                self.game_cell_button_pressed(game_cell)
                killed_other_tokens = token.killed_other_tokens
                if killed_other_tokens:
                    killed_token_names = []
                    for killed_token_id in token.killed_other_token_ids:
                        killed_token = board.get_token(killed_token_id)
                        killed_token_cell_id = killed_token.current_node.id
                        killed_token_home_cell = self.cell(killed_token_cell_id)
                        killed_token_names.append(
                            killed_token_home_cell.token_ids[killed_token_id]
                        )
                    killed_tokens_msg = "Killed: "
                    killed_tokens_msg += ", ".join(
                        token_name for token_name in killed_token_names
                    )
                    self.query_one("#header_msg").update(killed_tokens_msg)
                else:
                    self.query_one("#header_msg", Label).update(" ")
            else:
                self.query_one("#header_msg", Label).update(
                    "NO TOKEN YET IN PLAY!!!"
                )
        if not Game.DICE_ROLL == 6 and not killed_other_tokens:
            Game.CURRENT_HOUSE = Game.CURRENT_HOUSE.next_house

    def on_mount(self) -> None:
        """Get the game started when we first mount."""
        self.action_new_game()


class Ludo(App[None]):
    """Main 5x5 application class."""

    CSS_PATH = "ludo_game.tcss"
    """The name of the stylesheet for the app."""

    BINDINGS = [("ctrl+d", "toggle_dark", "Toggle Dark Mode")]
    """App-level bindings."""

    TITLE = "4x4 -- Ludo Master"
    """The title of the application."""

    def on_mount(self) -> None:
        """Set up the application on startup."""
        game = Game()
        self.push_screen(game)


if __name__ == "__main__":
    Ludo().run()
