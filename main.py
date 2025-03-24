"""Simple version of 4x4, developed for/with Textual."""

from __future__ import annotations

import time
import threading
from typing import TYPE_CHECKING
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Line, Color, Rectangle
from kivy.utils import get_color_from_hex
from kivy.metrics import dp, sp  # Added for scaling

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
BLACK = '#000000'

# Define common spacing and padding in dp for scaling
COMMON_SPACING = dp(5)
COMMON_PADDING = dp(10)
COMMON_FONT_SIZE = sp(10)  # Default scalable font size

VARIANT_COLORS = {
    "primary": get_color_from_hex("#007bff"),  # Blue (Primary)
    "success": get_color_from_hex("#28a745"),  # Green (Success)
    "error": get_color_from_hex("#dc3545"),  # Red (Error)
    "warning": get_color_from_hex("#ffc107"),  # Yellow (Warning)
    "default": get_color_from_hex("#d3d3d3"),  # Light Gray (Default)
}


class GameHeader(BoxLayout):
    """Displays game title and current game state."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = 1
        self.spacing = COMMON_SPACING
        self.padding = COMMON_PADDING

        self.label_refs = []  # Keep references for later width adjustment

        self.title_label = Label(text="4X4 -- Ludo Master", font_size=COMMON_FONT_SIZE, halign="left",
                                 size_hint=(0.2, 1))
        self.title_label.bind(size=self.title_label.setter('text_size'))  # So text aligns properly

        self.message_label = Label(text="DEMO GAME. AUTOPLAY ONLY. PRESS RUN GAME NOW!!!", font_size=COMMON_FONT_SIZE,
                                   halign="left", size_hint=(0.4, 1))
        self.message_label.bind(size=self.message_label.setter('text_size'))

        self.winner_house_label = Label(font_size=COMMON_FONT_SIZE, halign="left", size_hint=(0.15, 1))
        self.winner_house_label.bind(size=self.winner_house_label.setter('text_size'))

        self.current_house_label = Label(font_size=COMMON_FONT_SIZE, halign="left", size_hint=(0.15, 1))
        self.current_house_label.bind(size=self.current_house_label.setter('text_size'))

        self.dice_roll_label = Label(font_size=COMMON_FONT_SIZE, halign="right", size_hint=(0.1, 1))
        self.dice_roll_label.bind(size=self.dice_roll_label.setter('text_size'))

        self.add_widget(self.title_label)
        self.add_widget(self.message_label)
        self.add_widget(self.winner_house_label)
        self.add_widget(self.current_house_label)
        self.add_widget(self.dice_roll_label)


class GameFooter(BoxLayout):
    """Footer with control buttons."""

    def __init__(self, game_instance, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = 1
        self.orientation = 'horizontal'
        self.spacing = COMMON_SPACING
        self.padding = COMMON_PADDING
        self.game_instance = game_instance  # Reference to Game instance

        btn = Button(text=f"Run Game", font_size=COMMON_FONT_SIZE)
        self.add_widget(btn)

        btn.bind(on_press=self.run_game)

    def run_game(self, instance):
        """Calls the game loop when 'Run Game' button is pressed."""
        instance.disabled = True  # Disable the button
        self.game_instance.run_game_loop()  # Call Game's method


class GameCell(Button):
    """Represents an individual playable cell in the game."""

    @staticmethod
    def at(node_id: int) -> str:
        """Get the ID of the cell at the given location.

        Args:
            node_id (int): The node id of the cell.

        Returns:
            str: A string ID for the cell.
        """
        return f"cell-{node_id}"

    def __init__(self, **kwargs) -> None:
        """Initialise the game cell."""
        super().__init__(**kwargs)
        self.text = ""
        self.node_id = None
        self.token_ids = {}
        self.font_size = COMMON_FONT_SIZE

    def set_variant(self, variant):
        """Set the button's variant and update color"""
        if variant in VARIANT_COLORS:
            self.background_color = VARIANT_COLORS[variant]
        else:
            self.background_color = VARIANT_COLORS["default"]

    def reset_variant(self):
        """Reset the button to default"""
        self.set_variant("default")


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

    def __init__(self, **kwargs) -> None:
        """Initialise the game cell."""
        super().__init__(**kwargs)
        self.text = ""
        self.token_id = None
        self.font_size = COMMON_FONT_SIZE

    def update_border(self, *args):
        """Update the border of this specific cell."""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*get_color_from_hex(BLACK))
            Line(rectangle=(self.x, self.y, self.width, self.height), width=dp(1))

    def set_variant(self, variant):
        """Set the button's variant and update color"""
        if variant in VARIANT_COLORS:
            self.background_color = VARIANT_COLORS[variant]
        else:
            self.background_color = VARIANT_COLORS["default"]

    def reset_variant(self):
        """Reset the button to default"""
        self.set_variant("default")


# Custom House, GAME and END GridLayout with Background Color
class ColoredGridLayout(GridLayout):
    def __init__(self, color=None, rows=None, cols=None, house=None, end=None, game=None, border=None, **kwargs):
        super().__init__(**kwargs)
        self.rows = rows
        self.cols = cols
        self.spacing = COMMON_SPACING
        self.padding = COMMON_PADDING

        self.board = Game.BOARD
        self.house = house
        self.tokens = []
        self.token_locations = []
        self.end = end
        self.end_cells = []
        self.game = game
        self.game_cells = []

        if self.house:
            """Compose the game grid.

                Returns:
                    ComposeResult: The result of composing the game grid.
            """
            for row in range(Game.NUM_TOKENS):
                token_cell = GameCell()
                token_loc_cell = TokenLocationCell()
                self.tokens.append(token_cell)
                self.token_locations.append(token_loc_cell)
                self.add_widget(token_cell)
                self.add_widget(token_loc_cell)

        if self.end:
            """Compose the game grid.

                Returns:
                    ComposeResult: The result of composing the game grid.
            """
            indices = [1, 3, 5, 7]

            for i in range(Game.END_GRID_CELLS):
                if i in indices:
                    end_cell = GameCell()
                else:
                    end_cell = Label(color=BLACK, font_size=COMMON_FONT_SIZE)
                self.end_cells.append(end_cell)
                self.add_widget(end_cell)

        if self.game:
            """Compose the game grid.

                Returns:
                    ComposeResult: The result of composing the game grid.
            """
            for _, row in enumerate(range(Game.NUM_GRID_CELLS)):
                game_cell = GameCell()
                self.game_cells.append(game_cell)
                self.add_widget(game_cell)

        with self.canvas.before:
            # Set background color
            if color:
                Color(*get_color_from_hex(color))
            self.rect = Rectangle(size=self.size, pos=self.pos)

            # Add border with Slate Gray (#778899) color
            if not self.end:
                Color(*get_color_from_hex(GRID_BORDER if border else HOUSE_BORDER))  # Slate Gray
                self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=dp(1))

        self.bind(size=self.update_rect, pos=self.update_rect)  # Update size

    def update_rect(self, *args):
        """ Update"""
        self.rect.size = self.size
        self.rect.pos = self.pos
        if not self.end:
            self.border.rectangle = (self.x, self.y, self.width, self.height)

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
                game_cell.background_color = main_house_bg
                game_cell.node_id = start_house.get_start_node().id
            elif game_cell_index in house_indices:
                game_cell.background_color = main_house_bg
                house_index = house_indices.index(game_cell_index)
                game_cell.node_id = primary_house.house_nodes[house_index].id
            elif game_cell_index == fork_node_index:
                game_cell.background_color = WHITE
                game_cell.node_id = fork_house.get_fork_node().id
            elif game_cell_index == star_node_index:
                game_cell.background_color = star_node_bg
                game_cell.node_id = star_house.get_star_node().id
            elif game_cell_index in primary_house_regular_indices:
                game_cell.background_color = WHITE
                node_index = primary_house_regular_indices[game_cell_index]
                game_cell.node_id = primary_house.nodes[node_index].id
            else:
                game_cell.background_color = WHITE
                node_index = secondary_house_regular_indices[game_cell_index]
                game_cell.node_id = secondary_house.nodes[node_index].id
            game_cell.id = GameCell.at(game_cell.node_id)
            game_cell.text = f"{game_cell.node_id}"

    def get_game_cell(self, node_id: int) -> GameCell | None:
        """Find a cell by its ID.

        Args:
            node_id (int): The node ID of the cell.

        Returns:
            GameCell: The cell corresponding to the ID.
        """
        cell_id = GameCell.at(node_id)
        for cell in self.tokens:
            if hasattr(cell, "id") and cell.id == cell_id:
                return cell

        for cell in self.end_cells:
            if hasattr(cell, "id") and cell.id == cell_id:
                return cell

        for cell in self.game_cells:
            if hasattr(cell, "id") and cell.id == cell_id:
                return cell

    def get_token_location_cell(self, token_id: int) -> TokenLocationCell | None:
        """Find a TokenLocationCell by its ID.

        Args:
            token_id (int): The ID of the token.

        Returns:
            TokenLocationCell: The cell corresponding to the token ID.
        """
        cell_id = TokenLocationCell.at(token_id)
        for cell in self.token_locations:
            if hasattr(cell, "id") and cell.id == cell_id:
                return cell


class BlueHouseGrid(ColoredGridLayout):
    """Initialise style to Blue House grid."""

    def __init__(self):
        """Initialize style to Blue House tokens."""
        super().__init__(color=BLUE, rows=2, house=True)  # , size_hint=(0.2, 1)
        self.blue_house = self.board.blue_house
        blue_tokens = list(self.blue_house.tokens)
        for index, token in enumerate(self.tokens):
            token.background_color = BLUE
            blue_token = blue_tokens[index]
            token.node_id = blue_token.home_node.id
            token_label = f"B{index + 1}-{token.node_id}"
            token.text = token_label
            token.id = GameCell.at(token.node_id)
            token.token_ids[blue_token.id] = token_label

            token_loc = self.token_locations[index]
            token_loc.text = str(token.node_id)
            token_loc.color = 'black'
            token_loc.token_id = blue_token.id
            token_loc.id = TokenLocationCell.at(token_loc.token_id)


class RedHouseGrid(ColoredGridLayout):
    """Initialise style to Blue House grid."""

    def __init__(self):
        """Initialize style to Blue House tokens."""
        super().__init__(rows=2, color=RED, house=True)  # , size_hint=(0.2, 1)
        self.red_house = self.board.red_house
        red_tokens = list(self.red_house.tokens)
        for index, token in enumerate(self.tokens):
            token.background_color = RED
            red_token = red_tokens[index]
            token.node_id = red_token.home_node.id
            token_label = f"R{index + 1}-{token.node_id}"
            token.text = token_label
            token.id = GameCell.at(token.node_id)
            token.token_ids[red_token.id] = token_label

            token_loc = self.token_locations[index]
            token_loc.text = str(token.node_id)
            token_loc.color = 'black'
            token_loc.token_id = red_token.id
            token_loc.id = TokenLocationCell.at(token_loc.token_id)


class GreenHouseGrid(ColoredGridLayout):
    """Initialise style to Blue House grid."""

    def __init__(self):
        """Initialize style to Blue House tokens."""
        super().__init__(rows=2, color=GREEN, house=True)  # , size_hint=(0.2, 1)
        self.green_house = self.board.green_house
        green_tokens = list(self.green_house.tokens)
        for index, token in enumerate(self.tokens):
            token.background_color = GREEN
            green_token = green_tokens[index]
            token.node_id = green_token.home_node.id
            token_label = f"G{index + 1}-{token.node_id}"
            token.text = token_label
            token.id = GameCell.at(token.node_id)
            token.token_ids[green_token.id] = token_label

            token_loc = self.token_locations[index]
            token_loc.text = str(token.node_id)
            token_loc.color = 'black'
            token_loc.token_id = green_token.id
            token_loc.id = TokenLocationCell.at(token_loc.token_id)


class YellowHouseGrid(ColoredGridLayout):
    """Initialise style to Blue House grid."""

    def __init__(self):
        """Initialize style to Blue House tokens."""
        super().__init__(rows=2, color=YELLOW, house=True)  # , size_hint=(0.2, 1)
        self.yellow_house = self.board.yellow_house
        yellow_tokens = list(self.yellow_house.tokens)
        for index, token in enumerate(self.tokens):
            token.background_color = YELLOW
            yellow_token = yellow_tokens[index]
            token.node_id = yellow_token.home_node.id
            token_label = f"Y{index + 1}-{token.node_id}"
            token.text = token_label
            token.id = GameCell.at(token.node_id)
            token.token_ids[yellow_token.id] = token_label

            token_loc = self.token_locations[index]
            token_loc.text = str(token.node_id)
            token_loc.color = 'black'
            token_loc.token_id = yellow_token.id
            token_loc.id = TokenLocationCell.at(token_loc.token_id)


class EndGrid(ColoredGridLayout):
    """The main playable grid of end game cells."""

    def __init__(self):
        super().__init__(color='#000000', cols=3, end=True)

        for index, end_cell in enumerate(self.end_cells):
            end_cell.text = "End"
            if index == 1:
                end_cell.background_color = GREEN
                end_cell.node_id = self.board.green_house.get_end_node().id
                end_cell.id = GameCell.at(end_cell.node_id)
            elif index == 3:
                end_cell.background_color = RED
                end_cell.node_id = self.board.red_house.get_end_node().id
                end_cell.id = GameCell.at(end_cell.node_id)
            elif index == 5:
                end_cell.background_color = YELLOW
                end_cell.node_id = self.board.yellow_house.get_end_node().id
                end_cell.id = GameCell.at(end_cell.node_id)
            elif index == 7:
                end_cell.background_color = BLUE
                end_cell.node_id = self.board.blue_house.get_end_node().id
                end_cell.id = GameCell.at(end_cell.node_id)


class BlueVerticalGameGrid(ColoredGridLayout):
    """Initialise style to Blue Vertical game grid."""

    def __init__(self):
        """Initialize style to game cells."""
        super().__init__(rows=6, cols=3, game=True, border=True)  # , size_hint=(0.6, 1)
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


class RedHorizontalGameGrid(ColoredGridLayout):
    """Initialise style to Red Horizontal game grid."""

    def __init__(self):
        """Initialize style to game cells."""
        super().__init__(rows=3, cols=6, game=True, border=True)  # , size_hint=(0.6, 1)
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


class GreenVerticalGameGrid(ColoredGridLayout):
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

    def __init__(self):
        """Initialize style to game cells."""
        super().__init__(rows=6, cols=3, game=True, border=True)  # , size_hint=(0.6, 1)
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


class YellowHorizontalGameGrid(ColoredGridLayout):
    """Initialise style to Yellow Horizontal game grid."""

    def __init__(self):
        """Initialize style to game cells."""
        super().__init__(rows=3, cols=6, game=True, border=True)  # , size_hint=(0.6, 1)
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


class Game:
    """Main 5x5 game grid screen."""

    NUM_GRID_CELLS: Final = 18
    NUM_TOKENS: Final = 4
    END_GRID_CELLS: Final = 9
    BOARD = Board()
    CURRENT_HOUSE = BOARD.red_house
    DICE_ROLL = 0
    PREV_TOKEN_LOC_CELL = None
    PREV_TOKEN_LOC_CELL_VARIANT = None
    GAME_RUNNING = False

    def __init__(self):
        """Initialize game state and store references to UI grids."""
        self.game_header = GameHeader()  # Get GameHeader instance
        self.blue_house_grid = BlueHouseGrid()
        self.blue_grid = BlueVerticalGameGrid()
        self.red_house_grid = RedHouseGrid()
        self.red_grid = RedHorizontalGameGrid()
        self.green_house_grid = GreenHouseGrid()
        self.green_grid = GreenVerticalGameGrid()
        self.yellow_house_grid = YellowHouseGrid()
        self.yellow_grid = YellowHorizontalGameGrid()
        self.end_grid = EndGrid()

    def game_cell_button_pressed(self, game_cell: GameCell):
        """Play game when pressed the game cell."""
        if Game.PREV_TOKEN_LOC_CELL:
            Game.PREV_TOKEN_LOC_CELL.set_variant(Game.PREV_TOKEN_LOC_CELL_VARIANT)

        game_cell_msg = f"DICE ROLL: {Game.DICE_ROLL} "
        game_cell_msg += f"PRESSED {game_cell.node_id} "

        if len(game_cell.token_ids) > 0:
            game_cell_msg += f"[BEFORE]: with token ids {game_cell.token_ids}\n"
            board = Game.BOARD
            token_ids = list(game_cell.token_ids.keys())
            token_choice = randint(0, len(game_cell.token_ids) - 1)
            game_cell_msg += (
                f"[BEFORE]: select token choice {token_choice}  \n"
            )
            token_id = token_ids[token_choice]
            game_cell_msg += f"[BEFORE]: selected token id {token_id}  \n"
            token_label = game_cell.token_ids[token_id]
            token = board.get_token(token_id)
            token.move(Game.DICE_ROLL)

            del game_cell.token_ids[token_id]

            next_cell_id = token.current_node.id
            next_game_cell = self.get_game_cell_safely(next_cell_id)
            next_game_cell.token_ids[token_id] = token_label

            token_loc_cell = self.get_token_location_cell_safely(token_id)
            if token.reached_end():
                token_loc_cell.set_variant("success")
                token_loc_cell.text = "REACHED END"
                Game.PREV_TOKEN_LOC_CELL = None
            else:
                for killed_token_id in token.killed_other_token_ids:
                    killed_token = board.get_token(killed_token_id)
                    killed_token_cell = self.get_token_location_cell_safely(killed_token_id)
                    killed_token_cell_id = killed_token.current_node.id
                    killed_token_home_cell = self.get_game_cell_safely(killed_token_cell_id)
                    killed_token_home_cell.token_ids[
                        killed_token_id
                    ] = next_game_cell.token_ids[killed_token_id]
                    killed_token_cell.set_variant("error")
                    killed_token_cell.text = f"At: {killed_token_cell_id}"

                    del next_game_cell.token_ids[killed_token_id]
                    Game.PREV_TOKEN_LOC_CELL = None
                token_loc_cell.set_variant("warning")
                token_loc_cell.text = f"At: {next_cell_id}"
                Game.PREV_TOKEN_LOC_CELL = token_loc_cell
                Game.PREV_TOKEN_LOC_CELL_VARIANT = "primary"

            game_cell_msg += f"[AFTER] with token ids {game_cell.token_ids}\n"
            game_cell_msg += f"Next node is {next_cell_id} \n"
            game_cell_msg += (
                f"[AFTER] with token ids {next_game_cell.token_ids}\n"
            )
            game_cell_msg += (
                f"[AFTER] Token loc cell is {token_loc_cell.token_id} \n"
            )
        else:
            game_cell_msg += "with no tokens"

    def on_button_pressed(self, instance) -> None:
        """React to a press of a button on the game grid.

        Args:
            instance (Button): The event to react to.
        """
        if isinstance(instance, TokenLocationCell):
            return
        elif isinstance(instance, GameCell):
            self.game_cell_button_pressed(instance)

    def run_game_loop(self) -> None:
        """Run the game loop in a non-blocking thread."""
        if Game.GAME_RUNNING:
            return  # Prevent multiple threads from running simultaneously

        Game.GAME_RUNNING = True  # Mark game as running

        board = Game.BOARD

        def game_loop():
            """Game loop running in a background thread."""
            Clock.schedule_once(
                lambda dt: self.update_message(message="AUTO PLAYING NOW."))

            while not board.completed():
                self.play_next_move()
                time.sleep(0.33)  # Simulating game step delay

            # Game over message
            game_over_msg = "GAME OVER. THANK YOU. QUIT, RESTART TO PLAY ANOTHER GAME!!!"

            # Determine winner
            winner = "Blue" if board.winner_house.type == board.blue_house.type else \
                "Red" if board.winner_house.type == board.red_house.type else \
                    "Yellow" if board.winner_house.type == board.yellow_house.type else "Green"

            # Update UI labels
            # Update UI using Clock (UI updates must be on the main thread)
            Clock.schedule_once(
                lambda dt: self.update_message(winner=winner))

            Clock.schedule_once(lambda dt: self.update_message(current_house=""))

            Clock.schedule_once(lambda dt: self.update_message(dice_roll=""))

            Clock.schedule_once(
                lambda dt: self.update_message(message=game_over_msg))

            self.game_running = False  # Mark game as stopped

        # Run the game loop in a separate thread to prevent UI freezing
        game_thread = threading.Thread(target=game_loop, daemon=True)
        game_thread.start()

    def action_next_move(self):
        """Play the next move in a thread-safe way."""
        board = Game.BOARD
        if board.completed():
            game_over_msg = "GAME OVER. THANK YOU. QUIT, RESTART TO PLAY ANOTHER GAME!!!"

            # Determine winner
            winner = "Blue" if board.winner_house.type == board.blue_house.type else \
                "Red" if board.winner_house.type == board.red_house.type else \
                    "Yellow" if board.winner_house.type == board.yellow_house.type else "Green"

            # Update UI labels safely using Kivy Clock
            Clock.schedule_once(
                lambda dt: self.update_message(winner=f"Winner: {winner}"))

            Clock.schedule_once(lambda dt: self.update_message(current_house=""))

            Clock.schedule_once(lambda dt: self.update_message(dice_roll=""))

            Clock.schedule_once(
                lambda dt: self.update_message(message=game_over_msg))
        else:
            self.play_next_move()

    def play_next_move(self):
        """Play next move, update token positions, game cell, and labels."""
        current_house = Game.CURRENT_HOUSE  # Get the current house
        board = Game.BOARD  # Get the game board instance

        # Determine current house color
        house_color = "Blue" if current_house.type == board.blue_house.type else \
            "Red" if current_house.type == board.red_house.type else \
                "Yellow" if current_house.type == board.yellow_house.type else "Green"

        # Update the current house label safely
        Clock.schedule_once(
            lambda dt: self.update_message(current_house=f"Current house: {house_color}"))

        # Roll the dice
        Game.DICE_ROLL = randint(1, 6)
        Clock.schedule_once(
            lambda dt: self.update_message(dice_roll=f"    Dice Roll: {Game.DICE_ROLL}"))

        tokens_in_house = current_house.get_tokens_in_house()
        num_tokens_in_house = len(tokens_in_house)
        killed_other_tokens = False
        play_new_token = False

        # Logic for moving a new token if dice roll is 6
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
                game_cell = self.get_game_cell_safely(home_node_id)
                self.game_cell_button_pressed(game_cell)
                Clock.schedule_once(lambda dt: self.update_message(message=" "))
        else:
            tokens_in_play = current_house.get_token_ids_in_play()
            num_tokens_in_play = len(tokens_in_play)

            if num_tokens_in_play > 0:
                token_choice = randint(0, num_tokens_in_play - 1)
                token_id = tokens_in_play[token_choice]
                token = board.get_token(token_id)
                game_cell = self.get_game_cell_safely(token.current_node.id)
                self.game_cell_button_pressed(game_cell)

                killed_other_tokens = token.killed_other_tokens

                if killed_other_tokens:
                    killed_token_names = []
                    for killed_token_id in token.killed_other_token_ids:
                        killed_token = board.get_token(killed_token_id)
                        killed_token_cell_id = killed_token.current_node.id
                        killed_token_home_cell = self.get_game_cell_safely(killed_token_cell_id)
                        killed_token_names.append(killed_token_home_cell.token_ids[killed_token_id])

                    killed_tokens_msg = f"Killed: {', '.join(killed_token_names)}"
                    Clock.schedule_once(
                        lambda dt: self.update_message(message=killed_tokens_msg))
                else:
                    Clock.schedule_once(lambda dt: self.update_message(message=" "))
            else:
                Clock.schedule_once(
                    lambda dt: self.update_message(message="NO TOKEN YET IN PLAY!!!"))

        # If dice roll is not 6 and no tokens were killed, move to the next house
        if not Game.DICE_ROLL == 6 and not killed_other_tokens:
            Game.CURRENT_HOUSE = Game.CURRENT_HOUSE.next_house

    def update_message(self, message=None, winner=None, current_house=None, dice_roll=None):
        """Safely update the message label on the main thread."""
        if message:
            self.game_header.message_label.text = message  # Update UI safely
        if winner:
            self.game_header.winner_house_label.text = f"Winner: {winner}"
        if current_house:
            self.game_header.current_house_label.text = current_house
        if dice_roll:
            self.game_header.dice_roll_label.text = dice_roll

    def get_game_cell_safely(self, node_id: int):
        """Safely retrieve an existing `GameCell` from the board."""
        for grid in self.get_all_game_grids():
            game_cell = grid.get_game_cell(node_id)
            if game_cell:
                return game_cell

    def get_token_location_cell_safely(self, token_id: int):
        """Safely retrieve an existing 'TokenLocationCell' from the board."""
        for token in self.get_all_game_grids():
            token_cell = token.get_token_location_cell(token_id)
            if token_cell:
                return token_cell

    def get_all_game_grids(self):
        """Return all game grid instances."""
        return [self.blue_house_grid, self.blue_grid, self.red_house_grid, self.red_grid, self.green_house_grid,
                self.green_grid, self.yellow_house_grid, self.yellow_grid, self.end_grid]


class Ludo(App):
    """Main Ludo application class."""

    def build(self):
        self.title = "Ludo Master"  # This is for Dev env.
        self.icon = 'LudoIcon2.png'  # This is for Dev env.

        # Main vertical layout
        mainLayout = BoxLayout(orientation='vertical', spacing=COMMON_SPACING, padding=COMMON_PADDING)

        game_instance = Game()  # Create the game instance

        mainLayout.add_widget(game_instance.game_header)  # Add header

        # Top row: RedHouseGrid | GreenVerticalGameGrid | GreenHouseGrid
        topBoxLayout = BoxLayout(orientation='horizontal', spacing=COMMON_SPACING)
        topBoxLayout.add_widget(game_instance.red_house_grid)
        topBoxLayout.add_widget(game_instance.green_grid)
        topBoxLayout.add_widget(game_instance.green_house_grid)

        # Middle row: RedHorizontalGameGrid | EndGrid | YellowHorizontalGameGrid
        middleBoxLayout = BoxLayout(orientation='horizontal', spacing=COMMON_SPACING)
        middleBoxLayout.add_widget(game_instance.red_grid)
        middleBoxLayout.add_widget(game_instance.end_grid)
        middleBoxLayout.add_widget(game_instance.yellow_grid)

        # Bottom row: BlueHouseGrid | BlueVerticalGameGrid | YellowHouseGrid
        bottomBoxLayout = BoxLayout(orientation='horizontal', spacing=COMMON_SPACING)
        bottomBoxLayout.add_widget(game_instance.blue_house_grid)
        bottomBoxLayout.add_widget(game_instance.blue_grid)
        bottomBoxLayout.add_widget(game_instance.yellow_house_grid)

        # Add the three horizontal layouts to the main vertical layout
        mainLayout.add_widget(topBoxLayout)
        mainLayout.add_widget(middleBoxLayout)
        mainLayout.add_widget(bottomBoxLayout)

        mainLayout.add_widget(GameFooter(game_instance))  # Pass game instance to footer

        return mainLayout


if __name__ == '__main__':
    Ludo().run()