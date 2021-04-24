from bearlibterminal import terminal

from config import Config
from engine.map.components.board import Board
from engine.map.components.tile import Tile


class BoardConsole:

    def __init__(self, row, col):
        self._row = row
        self._col = col

    def render(self, board: Board):
        for tile in board.get_tiles():
            self._render(tile=tile)

    def _render_hint(self):
        terminal.clear_area(0, self._hint_row, 1000, 1)
        if self._hint_level == 0:
            return
        elif self._hint_level == 1:
            hint = self._move_hints[0]
        else:
            hint = str.format('{}{}', self._move_hints[0], self._move_hints[1])
        terminal.puts(self._col, self._hint_row, str.format('[color=gray][[Hint: {}]]', hint))

    def _render(self, tile: Tile):
        render_string = str.format("[font=chess][color={}][bkcolor={}]{}", tile.char_color,
                                   tile.bg_color, tile.char)
        self._render_board1(tile, render_string)
        self._render_board2(tile, render_string)

    def _render_board1(self, tile, string):
        terminal.puts(
            self._col + (tile.coordinate.col * Config.CHESS_FONT_SPACING_COL),
            self._row + (tile.coordinate.row * Config.CHESS_FONT_SPACING_ROW),
            string,
        )

    def _render_board2(self, tile, string):
        terminal.puts(
            self._col + (abs(tile.coordinate.col - 7) * Config.CHESS_FONT_SPACING_COL) + (
                    (8 + Config.BOARD_GAP) * Config.CHESS_FONT_SPACING_COL),
            self._row + (abs(tile.coordinate.row - 7) * Config.CHESS_FONT_SPACING_ROW),
            string,
        )
