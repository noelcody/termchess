import time
import traceback
from typing import Dict

from bearlibterminal import terminal

from debug import Debug
from engine.input.long_notation_parser import LongNotationParser
from engine.input.notation_parser import NotationParser, InvalidNotationException
from engine.map.components.board import Board, IllegalMoveException
from engine.map.util.player import Player
from engine.menu import MenuOption
from engine.render.board_console import BoardConsole
from engine.render.captures_console import CapturesConsole
from engine.render.text_console import TextConsole
from engine.stockfish import StockfishWrapper


class BackToMenuException(Exception):
    pass


class GameOverException(Exception):
    pass


class RetryMoveException(Exception):
    pass


class Game():
    HINT_KEY = terminal.TK_SLASH

    def __init__(self, board_con: BoardConsole, text_con: TextConsole, captures_con: CapturesConsole,
                 player_options: Dict[int, MenuOption]):
        self._player = 1
        self._captures = {1: [], 2: []}
        self._move_number = 0
        self._move_long_notations = []
        self._hint_level = 0
        self._show_score = False

        self._text_con = text_con
        self._text_con.set_player(self._player)
        self._captures_con = captures_con
        self._board_con: BoardConsole = board_con
        self._notation_parser = NotationParser()
        self._long_notation_parser = LongNotationParser()
        self._board: Board = Board(long_notation_parser=self._long_notation_parser)

        self._stockfish_lvl_by_player = dict()
        for player in player_options.keys():
            options = player_options[player]
            if not options.is_human:
                self._stockfish_lvl_by_player[player] = options.cpu_lvl
        self._stockfish = StockfishWrapper()

    def loop(self):
        self._render_move_start()
        self._make_move(self._get_move())
        self._render_move_end()
        self._prepare_for_next_move()

    def _render_move_start(self):
        self._board_con.render(self._board)
        self._captures_con.render(self._captures)
        self._text_con.set_evaluation(self._stockfish.get_evaluation())
        self._render_detail()
        terminal.refresh()

        next_best_move = self._long_notation_parser.parse_to_move(self._player, self._stockfish.get_best_move())
        # TODO
        # this takes a small but noticeable amount of time so render after refreshing everything else
        if self._board.is_in_check(self._player):
            self._text_con.render_status('check')
        terminal.refresh()

    def _get_move(self):
        if self._player not in self._stockfish_lvl_by_player:
            notation_input = self._read_input(10)
            try:
                move = self._notation_parser.parse_to_move(self._player, notation_input)
            except InvalidNotationException as e:
                terminal.clear()
                self._text_con.render_error(str.format('\'{}\' {}', notation_input, str(e)))
                traceback.print_exc()
                raise RetryMoveException()
        else:
            self._check_input()
            time.sleep(.5)
            long_notation_input = self._stockfish.get_move_at_lvl(self._stockfish_lvl_by_player[self._player])
            Debug.log(
                str.format('stockfish lvl {} (p{}): {}', self._stockfish_lvl_by_player[self._player], self._player,
                           long_notation_input))
            move = self._long_notation_parser.parse_to_move(self._player, long_notation_input)
        return move

    def _make_move(self, move):
        try:
            move_result = self._board.make_move(move, self._captures, self._move_number)
            self._move_long_notations.append(move_result.long_notation)
        except IllegalMoveException as e:
            terminal.clear()
            self._text_con.render_error(str.format('{}', str(e)))
            raise RetryMoveException()

    def _render_move_end(self):
        self._stockfish.set_position(self._move_long_notations)
        stockfish_evaluation = self._stockfish.get_evaluation()
        next_best_move = self._stockfish.get_best_move()
        # if player made a move and stockfish evaluates M0 that player just won
        if stockfish_evaluation['type'] == 'mate' and stockfish_evaluation['value'] == 0:
            self._gameover(str.format('checkmate! p{} wins (press any key)', self._player))
        # if player made a move and stockfish has no next best move then stalemate
        if next_best_move is None:
            self._gameover('stalemate! (press any key)')
        terminal.clear()

    def _gameover(self, message):
        terminal.clear()
        self._board_con.render(self._board)
        self._captures_con.render(self._captures)
        self._text_con.render_green(message)
        terminal.refresh()
        raise GameOverException()

    def _prepare_for_next_move(self):
        self._player = Player.other(self._player)
        self._text_con.set_player(self._player)
        self._move_number += 1

    def _read_input(self, max: int) -> str:
        input = ''
        while True:
            self._text_con.render_notation_input(input)
            key = terminal.read()
            if self._handle_meta_input(key):
                continue
            elif key == terminal.TK_RETURN:
                return input
            elif key == terminal.TK_BACKSPACE and len(input) > 0:
                input = input[:-1]
            elif terminal.check(terminal.TK_WCHAR) and len(input) < max:
                input += chr(terminal.state(terminal.TK_WCHAR))

    def _check_input(self):
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
        elif key == terminal.TK_CLOSE:
            raise SystemExit()
        elif key == terminal.TK_F1:
            self._show_score = not self._show_score
            self._render_detail()
            return True
        elif key == self.HINT_KEY:
            self._hint_level = min(self._hint_level + 1, 2)
            return True
        return False

    def _render_detail(self):
        if self._show_score:
            self._text_con.render_score()
        else:
            self._text_con.render_key_guide()
