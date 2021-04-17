from engine.input.coordinate_parser import CoordinateParser
from engine.map.components.coordinate import Coordinate


class CastleSpec:

    def __init__(self, player, is_kingside):
        if player == 1:
            if is_kingside:
                self.king_coord = CoordinateParser.to_coordinate('e1')
                self.rook_coord = CoordinateParser.to_coordinate('h1')
                self.passthru_coords = [CoordinateParser.to_coordinate('f1'), CoordinateParser.to_coordinate('g1')]
                self.dest_king_coord = CoordinateParser.to_coordinate('g1')
                self.dest_rook_coord = CoordinateParser.to_coordinate('f1')
            else:
                self.king_coord = CoordinateParser.to_coordinate('e1')
                self.rook_coord = CoordinateParser.to_coordinate('a1')
                self.passthru_coords = [CoordinateParser.to_coordinate('b1'), CoordinateParser.to_coordinate('c1'),
                                        CoordinateParser.to_coordinate('d1')]
                self.dest_king_coord = CoordinateParser.to_coordinate('c1')
                self.dest_rook_coord = CoordinateParser.to_coordinate('d1')
        elif player == 2:
            if is_kingside:
                self.king_coord = CoordinateParser.to_coordinate('e8')
                self.rook_coord = CoordinateParser.to_coordinate('h8')
                self.passthru_coords = [CoordinateParser.to_coordinate('f8'), CoordinateParser.to_coordinate('g8')]
                self.dest_king_coord = CoordinateParser.to_coordinate('g8')
                self.dest_rook_coord = CoordinateParser.to_coordinate('f8')
            else:
                self.king_coord = CoordinateParser.to_coordinate('e8')
                self.rook_coord = CoordinateParser.to_coordinate('a8')
                self.passthru_coords = [CoordinateParser.to_coordinate('b8'), CoordinateParser.to_coordinate('c8'),
                                        CoordinateParser.to_coordinate('d8')]
                self.dest_king_coord = CoordinateParser.to_coordinate('c8')
                self.dest_rook_coord = CoordinateParser.to_coordinate('d8')
        else:
            raise SystemError()


SPECS = [CastleSpec(1, True), CastleSpec(1, False), CastleSpec(2, True), CastleSpec(2, False)]


def get_castle_spec_for_king_coords(king_start_coord: Coordinate, king_dest_coord: Coordinate):
    for spec in SPECS:
        if spec.king_coord == king_start_coord and spec.dest_king_coord == king_dest_coord:
            return spec
    raise SystemError()
