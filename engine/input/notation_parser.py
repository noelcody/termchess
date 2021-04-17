from engine.input.coordinate_parser import CoordinateParser
from engine.input.invalid_notation_exception import InvalidNotationException
from engine.map.components.move import Move
from engine.map.components.piece import Pawn, NOTATION_TO_PIECE_TYPE


class NotationParser:
    def parse_to_move(self, player: int, notation: str) -> Move:
        try:
            if not notation or len(notation) == 0:
                raise InvalidNotationException()
            if notation[0].islower():
                return self._parse_pawn(player, notation)
            if notation[0] == '0' or notation[0] == 'O':
                return self._parse_castle(player, notation)
            else:
                return self._parse_piece(player, notation)
        except Exception as e:
            raise InvalidNotationException(e)

    def _parse_pawn(self, player, notation):
        orig_notation = notation
        is_capture = False
        start_col = None
        promotion_piece_type = None
        if notation[1] == 'x':
            is_capture = True
            start_col = CoordinateParser.to_coordinate_col(notation[0])
            notation = notation[2:]
        if len(notation) > 2 and notation[2] == '=':
            promotion_piece_type = NOTATION_TO_PIECE_TYPE[notation[3]]
            notation = notation[:-2]
        return Move.normal(notation=orig_notation, player=player, piece_type=Pawn,
                           dest_coord=CoordinateParser.to_coordinate(notation=notation), is_capture=is_capture,
                           start_col=start_col, promotion_piece=promotion_piece_type)

    def _parse_castle(self, player, notation):
        if notation == '0-0' or notation == 'O-O':
            return Move.castle_kingside(notation=notation, player=player)
        if notation == '0-0-0' or notation == 'O-O-O':
            return Move.castle_queenside(notation=notation, player=player)
        raise InvalidNotationException('use 0-0 or 0-0-0 to castle')

    def _parse_piece(self, player, notation):
        orig_notation = notation
        # first char is always the piece
        piece_char = notation[0]
        if piece_char not in NOTATION_TO_PIECE_TYPE.keys():
            raise InvalidNotationException(piece_char + ' is not a piece')
        piece_type = NOTATION_TO_PIECE_TYPE[piece_char]
        notation = notation[1:]

        # last 2 chars are always the dest coordinate
        dest_coord_notation = notation[-2:]
        dest_coord = CoordinateParser.to_coordinate(notation=dest_coord_notation)
        notation = notation[:-2]

        # capture notation if it exists
        if notation and notation[-1] == 'x':
            is_capture = True
            notation = notation[:-1]
        else:
            is_capture = False

        # whatever is left is disambiguation as rank and/or file
        start_row = None
        start_col = None
        if notation:
            if len(notation) > 2:
                raise InvalidNotationException()
            elif len(notation) == 2:
                disambiguation_coord = CoordinateParser.to_coordinate(notation=notation)
                start_row = disambiguation_coord.row
                start_col = disambiguation_coord.col
            else:
                try:
                    start_row = CoordinateParser.to_coordinate_row(notation[0])
                except:
                    start_col = CoordinateParser.to_coordinate_col(notation[0])

        return Move.normal(notation=orig_notation, player=player, piece_type=piece_type,
                           dest_coord=dest_coord, is_capture=is_capture,
                           start_row=start_row, start_col=start_col)
