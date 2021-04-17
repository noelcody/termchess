from typing import List


class Coordinate():

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col

    def __str__(self):
        return str.format("Coordinate(row={}, col={})", self.row, self.col)

    def __key(self):
        return (self.row, self.col)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Coordinate):
            return self.__key() == other.__key()
        return NotImplemented

    def get_straight_path(self, other: 'Coordinate') -> List['Coordinate']:
        if self.row == other.row:
            return [Coordinate(self.row, col) for col in range(min(self.col, other.col) + 1, max(self.col, other.col))]
        if self.col == other.col:
            return [Coordinate(row, self.col) for row in range(min(self.row, other.row) + 1, max(self.row, other.row))]
        raise Exception

    def get_diag_path(self, other: 'Coordinate') -> List['Coordinate']:
        if abs(self.row - other.row) != abs(self.col - other.col):
            raise Exception
        if self.row < other.row:
            if self.col < other.col:
                return [Coordinate(self.row + offset, self.col + offset) for offset in range(1, other.row - self.row)]
            else:
                return [Coordinate(self.row + offset, self.col - offset) for offset in range(1, other.row - self.row)]
        else:
            if other.col < self.col:
                return [Coordinate(other.row + offset, other.col + offset) for offset in range(1, self.row - other.row)]
            else:
                return [Coordinate(other.row + offset, other.col - offset) for offset in range(1, self.row - other.row)]
