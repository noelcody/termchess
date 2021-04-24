# https://pypi.org/project/stockfish/
from stockfish import Stockfish

from debug import Debug

MAX_LVL = 20


class StockfishWrapper:
    def __init__(self):
        self._stockfish = Stockfish("./stockfish")
        Debug.log(self._stockfish.get_parameters())

    def set_position(self, long_notations):
        self._stockfish.set_position(long_notations)

    def get_evaluation(self):
        self._stockfish.set_skill_level(MAX_LVL)
        return self._stockfish.get_evaluation()

    def get_best_move(self):
        self._stockfish.set_skill_level(MAX_LVL)
        return self._stockfish.get_best_move()

    def get_move_at_lvl(self, lvl: int):
        self._stockfish.set_skill_level(lvl)
        return self._stockfish.get_best_move()
