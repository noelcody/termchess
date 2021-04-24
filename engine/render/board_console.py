from typing import Tuple

from bearlibterminal import terminal

from config import Config
from engine.map.components.board import Board
from engine.map.components.coordinate import Coordinate
from engine.map.components.tile import Tile


class BoardConsole:

    def __init__(self, row, col):
        self._row = row
        self._col = col

    def render(self, board: Board):
        for tile in board.get_tiles():
            self._render(tile=tile)

    def set_hint_coords(self, coords: Tuple[Coordinate, Coordinate]):
        self._hint_coords = coords

    def render_hint(self, hint_level, board: Board):
        if hint_level == 0:
            return
        if hint_level >= 1:
            start_tile = board.get_tile_at(self._hint_coords[0])
            start_tile.bg_color = Config.HIGHLIGHT_SQ_COLOR
            self._render(start_tile)
        if hint_level == 2:
            dest_tile = board.get_tile_at(self._hint_coords[1])
            dest_tile.bg_color = Config.HIGHLIGHT_SQ_COLOR
            self._render(dest_tile)

    def _render(self, tile: Tile):
        render_string = str.format("[font=chess][color={}][bkcolor={}]{}", tile.char_color,
                                   tile.bg_color, tile.char)
        self._render_board1(tile, render_string)
        self._render_board2(tile, render_string)

    def _render_board1(self, tile, string):
        col = self._col + (tile.coordinate.col * Config.CHESS_FONT_SPACING_COL)
        row = self._row + (tile.coordinate.row * Config.CHESS_FONT_SPACING_ROW)
        terminal.clear_area(col, row, 1, 1)
        terminal.puts(col, row, string)

    def _render_board2(self, tile, string):
        col = self._col + (abs(tile.coordinate.col - 7) * Config.CHESS_FONT_SPACING_COL) + (
                (8 + Config.BOARD_GAP) * Config.CHESS_FONT_SPACING_COL)
        row = self._row + (abs(tile.coordinate.row - 7) * Config.CHESS_FONT_SPACING_ROW)
        terminal.clear_area(col, row, 1, 1)
        terminal.puts(col, row, string)
