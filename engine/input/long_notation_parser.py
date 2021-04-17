from typing import Optional

from engine.input.coordinate_parser import CoordinateParser
from engine.map.components.coordinate import Coordinate
from engine.map.components.move import Move
from engine.map.components.piece import Piece, PIECE_TYPE_TO_NOTATION, NOTATION_TO_PIECE_TYPE


class LongNotationParser:
    def parse_to_move(self, player, long_notation_input):
        if len(long_notation_input) > 5:
            raise SystemError('unexpected long notation format')
        start_coord = CoordinateParser.to_coordinate(long_notation_input[:2])
        dest_coord = CoordinateParser.to_coordinate(long_notation_input[2:4])
        if len(long_notation_input) == 5:
            promotion_piece_type = NOTATION_TO_PIECE_TYPE[long_notation_input[-1].upper()]
        else:
            promotion_piece_type = None
        return Move.exact(player=player, start_coord=start_coord, dest_coord=dest_coord,
                          promotion_piece_type=promotion_piece_type)

    def parse_to_long_notation(self, start_coord: Coordinate, dest_coord: Coordinate,
                               promotion_piece_type: Optional[Piece]):
        return str.format('{}{}{}', CoordinateParser.to_notation(start_coord),
                          CoordinateParser.to_notation(dest_coord),
                          PIECE_TYPE_TO_NOTATION[promotion_piece_type].lower() if promotion_piece_type else '')
