from bearlibterminal import terminal

from config import Config


class CapturesConsole():

    def __init__(self, row: int, col: int):
        self._row = row
        self._col = col

    def render_blank(self):
        self.render('')

    def render(self, captures):
        terminal.puts(
            self._col, self._row,
            self._render_player_captures(1, captures[1]),
        )
        terminal.puts(
            self._col + ((8 + Config.BOARD_GAP) * Config.CHESS_FONT_SPACING_COL), self._row,
            self._render_player_captures(2, captures[2]),
        )

    def _render_player_captures(self, player, player_captures):
        if not player_captures:
            return '[[0]]'
        capture_chars = [piece.empty_char if player == 1 else piece.char for piece in player_captures]
        total_value = sum([piece.piece_value for piece in player_captures])
        return str.format('[[{}]]: [font=captures][color=white]{}', total_value, ''.join(capture_chars))
