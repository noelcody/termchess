import time
import traceback
from typing import Dict

from bearlibterminal import terminal
# https://pypi.org/project/stockfish/
from stockfish import Stockfish

from debug import Debug
from engine.input.long_notation_parser import LongNotationParser
from engine.input.notation_parser import NotationParser, InvalidNotationException
from engine.map.components.board import Board, IllegalMoveException
from engine.map.util.player import Player
from engine.menu import MenuOption
from engine.render.board_console import BoardConsole
from engine.render.captures_console import CapturesConsole
from engine.render.text_console import TextConsole


class GameOverException(Exception):
    pass


class Game():
    def __init__(self, board_con: BoardConsole, text_con: TextConsole, captures_con: CapturesConsole,
                 player_options: Dict[int, MenuOption]):
        self._player = 1
        self._captures = {1: [], 2: []}
        self._move_number = 0
        self._move_long_notations = []

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
        self._stockfish = Stockfish("./stockfish")
        Debug.log(self._stockfish.get_parameters())

    def loop(self):
        # SETUP
        self._board_con.render(self._board)
        self._captures_con.render(self._captures)
        self._text_con.set_evaluation(self._stockfish.get_evaluation())
        self._text_con.render_detail()
        terminal.refresh()
        if self._board.is_in_check(self._player):
            self._text_con.render_status('check')
        terminal.refresh()

        # PARSE MOVE
        if self._player not in self._stockfish_lvl_by_player:
            notation_input = self._text_con.get_input()
            try:
                move = self._notation_parser.parse_to_move(self._player, notation_input)
            except InvalidNotationException as e:
                terminal.clear()
                self._text_con.render_error(str.format('\'{}\' {}', notation_input, str(e)))
                traceback.print_exc()
                return  # next loop
        else:
            self._text_con.check_input()
            self._stockfish.set_skill_level(self._stockfish_lvl_by_player[self._player])
            time.sleep(.5)
            long_notation_input = self._stockfish.get_best_move()
            Debug.log(str.format('stockfish lvl {} (p{}): {}', self._stockfish_lvl_by_player[self._player], self._player,
                             long_notation_input))
            move = self._long_notation_parser.parse_to_move(self._player, long_notation_input)

        # MAKE MOVE
        try:
            move_result = self._board.make_move(move, self._captures, self._move_number)
            self._move_long_notations.append(move_result.long_notation)
        except IllegalMoveException as e:
            terminal.clear()
            self._text_con.render_error(str.format('{}', str(e)))
            return  # next loop

        # COMPLETE
        self._stockfish.set_position(self._move_long_notations)
        stockfish_evaluation = self._stockfish.get_evaluation()
        next_best_move = self._stockfish.get_best_move()
        # if player made a move and stockfish evaluates M0 that player just won
        if stockfish_evaluation['type'] == 'mate' and stockfish_evaluation['value'] == 0:
            self._gameover(str.format('checkmate! p{} wins (press any key)', self._player))
        # if player made a move and stockfish has no next best move then stalemate
        if next_best_move is None:
            self._gameover('stalemate! (press any key)')
        self._next_move()
        terminal.clear()

    def _gameover(self, message):
        terminal.clear()
        self._board_con.render(self._board)
        self._captures_con.render(self._captures)
        self._text_con.render_green(message)
        terminal.refresh()
        raise GameOverException()

    def _next_move(self):
        self._player = Player.other(self._player)
        self._text_con.set_player(self._player)
        self._move_number += 1
