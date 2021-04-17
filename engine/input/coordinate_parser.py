from engine.input.invalid_notation_exception import InvalidNotationException
from engine.map.components.coordinate import Coordinate


class CoordinateParser:

    @staticmethod
    def to_coordinate(notation: str) -> 'Coordinate':
        if len(notation) != 2:
            raise InvalidNotationException("can't parse " + notation)
        col = CoordinateParser.to_coordinate_col(notation[0])
        row = CoordinateParser.to_coordinate_row(notation[1])
        return Coordinate(row=row, col=col)

    @staticmethod
    def to_coordinate_col(notation_file: str) -> int:
        col = ord(notation_file) - ord('a')
        if col < 0 or col > 7:
            raise InvalidNotationException('out of bounds')
        return col

    @staticmethod
    def to_coordinate_row(notation_rank: str) -> int:
        row = int(notation_rank) - 1
        if row < 0 or row > 7:
            raise InvalidNotationException('out of bounds')
        # flip row: chess indexes bottom to top
        return abs(row - 7)

    @staticmethod
    def to_notation(coord: Coordinate):
        '''
        coordinate to chess notation
        '''
        return str.format('{}{}', chr(ord('a') + coord.col), abs(coord.row - 7) + 1)
