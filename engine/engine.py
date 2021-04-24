from bearlibterminal import terminal

from config import Config
from engine.game import Game, GameOverException, BackToMenuException, RetryMoveException
from engine.menu import Menu, GameStartException
from engine.render.board_console import BoardConsole
from engine.render.captures_console import CapturesConsole
from engine.render.text_console import TextConsole

COLS = 112
ROWS = 40


class Engine():

    def run(self):
        terminal.open()
        terminal.composition(terminal.TK_ON)
        terminal.set(str.format("window.size={}x{}", COLS, ROWS))
        terminal.set(
            str.format("chess font: CASEFONT.ttf, size={}, spacing={}x{}",
                       Config.CHESS_FONT_SIZE,
                       Config.CHESS_FONT_SPACING_COL,
                       Config.CHESS_FONT_SPACING_ROW))
        terminal.set(
            str.format("captures font: CASEFONT.ttf, size={}, spacing=2x1", Config.CAPTURES_FONT_SIZE))
        terminal.color("white")
        while True:
            self._run_game()

    def _run_game(self):
        menu = Menu(row=18, col=49)
        while True:
            try:
                menu.loop()
            except GameStartException as e:
                player_options = e.player_options
                break
        terminal.clear()
        board_con = BoardConsole(row=2, col=5)
        text_con = TextConsole(row=Config.TEXT_CON_ROW, col=5)
        captures_con = CapturesConsole(row=Config.CAPTURES_CON_ROW, col=5)
        game = Game(board_con=board_con, text_con=text_con, captures_con=captures_con, player_options=player_options)
        while True:
            try:
                game.loop()
            except RetryMoveException:
                continue
            except GameOverException:
                # wait for any input
                key = terminal.read()
                if key == terminal.TK_CLOSE:
                    raise SystemExit()
                break
            except BackToMenuException:
                break
