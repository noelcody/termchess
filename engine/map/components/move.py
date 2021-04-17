from typing import Type, Optional

from engine.map.components.coordinate import Coordinate
from engine.map.components.piece import Piece


class Move:
    @staticmethod
    def castle_kingside(notation, player):
        return Move(notation, player, is_castle_kingside=True)

    @staticmethod
    def castle_queenside(notation, player):
        return Move(notation, player, is_castle_queenside=True)

    @staticmethod
    def normal(notation, player, piece_type: Optional[Type[Piece]], dest_coord: Optional[Coordinate], is_capture: bool,
               start_col=None, promotion_piece=None, start_row=None):
        return Move(notation=notation, player=player, piece_type=piece_type, dest_coord=dest_coord,
                    is_capture=is_capture,
                    start_col=start_col, promotion_piece_type=promotion_piece, start_row=start_row)

    @staticmethod
    def exact(player, start_coord: Coordinate, dest_coord: Coordinate, promotion_piece_type: Optional[Type[Piece]]):
        return Move(notation=None, player=player, long_notation_start_coord=start_coord, dest_coord=dest_coord,
                    promotion_piece_type=promotion_piece_type)

    def __init__(self, notation: str, player: int, piece_type: Optional[Type[Piece]] = None,
                 dest_coord: Optional[Coordinate] = None,
                 is_castle_kingside=False, is_castle_queenside=False, is_capture=False, start_col=None,
                 promotion_piece_type=None, start_row=None, long_notation_start_coord=None):
        self.notation = notation
        self.player = player
        self.piece_type = piece_type
        self.dest_coord = dest_coord
        self.is_castle_kingside = is_castle_kingside
        self.is_castle_queenside = is_castle_queenside
        self.is_capture = is_capture
        self.start_col = start_col
        self.start_row = start_row
        self.promotion_piece_type = promotion_piece_type
        self.long_notation_start_coord = long_notation_start_coord

    def __str__(self):
        return str.format(
            "Move(player={}, piece_type={}, new_coordinates={}, is_castle_kingside={}, is_castle_queenside={})",
            str(self.player), str(self.piece_type), str(self.dest_coord), str(self.is_castle_kingside),
            str(self.is_castle_queenside))
