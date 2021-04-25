from bearlibterminal import terminal

from config import Config


class TextConsole():

    def __init__(self, row: int, col: int):
        self._row = row
        self._col = col
        self._detail_row = row + 7

    def set_player(self, player):
        self._player = player

    def set_evaluation(self, evaluation):
        self._evaluation = evaluation

    def render_notation_input(self, input):
        terminal.clear_area(0, Config.TEXT_CON_ROW, 1000, 1)
        terminal.puts(self._col + self._get_offset(), Config.TEXT_CON_ROW,
                      str.format('p{} move: {}█', self._player, input, chr(219)))
        terminal.refresh()

    def render_error(self, error):
        terminal.puts(
            self._col + self._get_offset(), self._row + 1,
            str.format('[color={}]error: {}', Config.RED_COLOR, error),
        )

    def render_green(self, message):
        terminal.puts(
            self._col + self._get_offset(), self._row,
            str.format('[color={}]{}', Config.GREEN_COLOR, message),
        )

    def render_status(self, status):
        terminal.puts(
            self._col + self._get_offset(), self._row - 1,
            str.format('[color=gray][[{}]]', status),
        )

    def render_score(self):
        self._clear_detail()
        if self._evaluation['type'] == 'cp':
            evaluation = self._evaluation['value'] / 100
            if evaluation > 0:
                prefix = '+'
            else:
                prefix = ''
            terminal.puts(
                self._col, self._detail_row,
                str.format('[color=gray][[{}{}]]', prefix, evaluation),
            )
        elif self._evaluation['type'] == 'mate':
            evaluation = self._evaluation['value']
            terminal.puts(
                self._col, self._detail_row,
                str.format('[color=gray][[M{}]]', evaluation),
            )
        terminal.refresh()

    def render_key_guide(self):
        self._clear_detail()
        terminal.puts(
            self._col, self._detail_row,
            str.format('[color=gray][[ESC: Return to menu]] [[F1: Show engine score]] [[/: Show move hint]] [[.: Highlight weak pieces]]'),
        )
        terminal.refresh()

    def _clear_detail(self):
        terminal.clear_area(0, self._detail_row, 1000, 1)

    def _get_offset(self):
        if self._player == 2:
            offset = (8 + Config.BOARD_GAP) * Config.CHESS_FONT_SPACING_COL
        else:
            offset = 0
        return offset
