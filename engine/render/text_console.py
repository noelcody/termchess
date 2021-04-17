from bearlibterminal import terminal

from config import Config


class BackToMenuException(Exception):
    pass


class TextConsole():
    PROMPT_LEN = 14

    def __init__(self, row: int, col: int):
        self._row = row
        self._col = col

    def render_green(self, message):
        terminal.puts(
            self._col + self._get_offset(), self._row,
            str.format('[color={}]{}', 'green', message),
        )

    def render_error(self, error):
        terminal.puts(
            self._col + self._get_offset(), self._row + 1,
            str.format('[color={}]error: {}', Config.RED_COLOR, error),
        )

    def render_status(self, status):
        terminal.puts(
            self._col + self._get_offset(), self._row - 1,
            str.format('[color=gray][[{}]]', status),
        )

    def set_player(self, player):
        self._player = player

    def get_input(self):
        return self._read_str(10)

    def _get_offset(self):
        if self._player == 2:
            offset = (8 + Config.BOARD_GAP) * Config.CHESS_FONT_SPACING_COL
        else:
            offset = 0
        return offset

    def set_evaluation(self, evaluation):
        self._evaluation = evaluation

    def render_detail(self):
        row = self._row + 7
        terminal.clear_area(0, row, 1000, 1)
        if Config.SHOW_SCORE and self._evaluation:
            if self._evaluation['type'] == 'cp':
                evaluation = self._evaluation['value'] / 100
                if evaluation > 0:
                    prefix = '+'
                else:
                    prefix = ''
                terminal.puts(
                    self._col, row,
                    str.format('[color=gray][[{}{}]]', prefix, evaluation),
                )
            elif self._evaluation['type'] == 'mate':
                evaluation = self._evaluation['value']
                terminal.puts(
                    self._col, row,
                    str.format('[color=gray][[M{}]]', evaluation),
                )
        else:
            terminal.puts(
                self._col, row,
                str.format('[color=gray][[ESC: Return to menu]] [[F1: Show engine score]]'),
            )
        terminal.refresh()

    def _read_str(self, max: int) -> str:
        input = ''
        while True:
            terminal.clear_area(0, Config.TEXT_CON_ROW, 1000, 1)
            terminal.puts(self._col + self._get_offset(), Config.TEXT_CON_ROW,
                          str.format('p{} move: {}█', self._player, input, chr(219)))
            terminal.refresh()
            key = terminal.read()
            self._handle_meta_input(key)
            if key == terminal.TK_RETURN:
                return input
            elif key == terminal.TK_BACKSPACE and len(input) > 0:
                input = input[:-1]
            elif terminal.check(terminal.TK_WCHAR) and len(input) < max:
                input += chr(terminal.state(terminal.TK_WCHAR))

    def check_input(self):
        '''
        allow interrupt for a cpu vs cpu game
        '''
        if not terminal.has_input():
            return
        key = terminal.read()
        self._handle_meta_input(key)

    def _handle_meta_input(self, key):
        if key == terminal.TK_ESCAPE:
            raise BackToMenuException()
        if key == terminal.TK_CLOSE:
            raise SystemExit()
        if key == terminal.TK_F1:
            Config.SHOW_SCORE = not Config.SHOW_SCORE
            self.render_detail()
