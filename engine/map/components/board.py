from typing import List, Tuple

from engine.input.coordinate_parser import CoordinateParser
from engine.input.long_notation_parser import LongNotationParser
from engine.map.components.coordinate import Coordinate
from engine.map.components.move import Move
from engine.map.components.move_result import MoveResult
from engine.map.components.piece import *
from engine.map.components.tile import Tile
from engine.map.util.castle_spec import CastleSpec, get_castle_spec_for_king_coords
from engine.map.util.player import Player
from engine.map.components.tile_map import TileGenerator

NON = Empty()


class IllegalMoveException(Exception):
    pass


class Board:
    def __init__(self, long_notation_parser: LongNotationParser):
        self._long_notation_parser = long_notation_parser
        self._board_array = [[R_B(), N_B(), B_B(), Q_B(), K_B(), B_B(), N_B(), R_B()],
                             [P_B(), P_B(), P_B(), P_B(), P_B(), P_B(), P_B(), P_B()],
                             [NON, NON, NON, NON, NON, NON, NON, NON],
                             [NON, NON, NON, NON, NON, NON, NON, NON],
                             [NON, NON, NON, NON, NON, NON, NON, NON],
                             [NON, NON, NON, NON, NON, NON, NON, NON],
                             [P_W(), P_W(), P_W(), P_W(), P_W(), P_W(), P_W(), P_W()],
                             [R_W(), N_W(), B_W(), Q_W(), K_W(), B_W(), N_W(), R_W()]]
        self._tile_generator = TileGenerator()
        self._refresh_tiles()

    def _copy_board_array(self):
        return [row[:] for row in self._board_array]

    def _refresh_tiles(self):
        self._tile_generator.refresh_tiles(self._board_array)

    def get_tiles(self):
        return self._tile_generator.get_tiles()

    def get_tile_at(self, coord: Coordinate) -> Tile:
        return self._tile_generator.get_tile_at(coord)

    def get_weak_coords(self, player) -> List[Coordinate]:
        '''
        Return weak coordinates for this player
        '''
        weak_coords = []
        for coord in self._yield_coordinates():
            piece = self._piece_at(coord)
            if piece is None or piece.player != player:
                continue
            if not self._does_player_target(player, [coord]):
                weak_coords.append(coord)
        return weak_coords

    def make_move(self, move: Move, captures, move_number: int) -> MoveResult:
        if move.long_notation_start_coord:
            start_coord, dest_coord = self._make_exact_move(move, captures, move_number)
        elif move.is_castle_kingside:
            start_coord, dest_coord = self._make_castle(move.player, CastleSpec(move.player, is_kingside=True))
        elif move.is_castle_queenside:
            start_coord, dest_coord = self._make_castle(move.player, CastleSpec(move.player, is_kingside=False))
        else:
            start_coord, dest_coord = self._make_move(move, captures, move_number)
        self._refresh_tiles()
        return MoveResult(long_notation=self._long_notation_parser.parse_to_long_notation(start_coord, dest_coord,
                                                                                          move.promotion_piece_type))

    def is_in_check(self, player):
        return self._does_player_target(Player.other(player), [self._get_king_coord(player)])

    def _make_exact_move(self, move, captures, move_number):
        # check for castle notation
        maybe_king = self._piece_at(move.long_notation_start_coord)
        if isinstance(maybe_king, King) and abs(move.long_notation_start_coord.col - move.dest_coord.col) > 1:
            self._make_castle(move.player, castle_spec=get_castle_spec_for_king_coords(
                king_start_coord=move.long_notation_start_coord, king_dest_coord=move.dest_coord))
        else:  # this is a normal move
            self._commit_move(move.player, move.long_notation_start_coord, move.dest_coord, move.promotion_piece_type,
                              captures, move_number)
        return (move.long_notation_start_coord, move.dest_coord)

    def _make_castle(self, player, castle_spec: CastleSpec) -> Tuple[Coordinate, Coordinate]:
        self._validate_castle(player, castle_spec)
        self._commit_castle(castle_spec)
        return (castle_spec.king_coord, castle_spec.dest_king_coord)

    def _validate_castle(self, player, castle_spec):
        if not isinstance(self._piece_at(castle_spec.king_coord), King):
            raise IllegalMoveException('king out of position to castle')
        if self._piece_at(castle_spec.king_coord).has_moved:
            raise IllegalMoveException('king has already moved')
        if not isinstance(self._piece_at(castle_spec.rook_coord), Rook):
            raise IllegalMoveException('rook out of position to castle')
        if self._piece_at(castle_spec.rook_coord).has_moved:
            raise IllegalMoveException('rook has already moved')
        if not self._is_unobstructed(castle_spec.passthru_coords):
            raise IllegalMoveException('castle path is blocked')
        all_king_coords = Coordinate.get_straight_path(castle_spec.king_coord, castle_spec.dest_king_coord)
        all_king_coords.extend([castle_spec.king_coord, castle_spec.dest_king_coord])
        if self._does_player_target(Player.other(player), all_king_coords):
            raise IllegalMoveException('king would move through or into check')

    def _commit_castle(self, castle_spec):
        self._board_array[castle_spec.dest_king_coord.row][castle_spec.dest_king_coord.col] = \
            self._board_array[castle_spec.king_coord.row][castle_spec.king_coord.col]
        self._board_array[castle_spec.king_coord.row][castle_spec.king_coord.col] = NON
        self._board_array[castle_spec.dest_rook_coord.row][castle_spec.dest_rook_coord.col] = \
            self._board_array[castle_spec.rook_coord.row][castle_spec.rook_coord.col]
        self._board_array[castle_spec.rook_coord.row][castle_spec.rook_coord.col] = NON

    def _make_move(self, move, captures, move_number) -> Tuple[Coordinate, Coordinate]:
        if move.player == self._piece_at(move.dest_coord).player:
            raise IllegalMoveException(str.format('{} is occupied', CoordinateParser.to_notation(move.dest_coord)))
        if move.piece_type == Pawn and move.is_capture:
            is_en_passant = self._maybe_get_enpassant_pawn_coord(player=move.player, coord=move.dest_coord,
                                                                 move_number=move_number) != None
            if self._piece_at(move.dest_coord) is NON and not is_en_passant:
                raise IllegalMoveException(
                    str.format('nothing to capture on {}', CoordinateParser.to_notation(move.dest_coord)))
        elif move.is_capture and self._piece_at(move.dest_coord) is NON:
            raise IllegalMoveException(
                str.format('nothing to capture on {}', CoordinateParser.to_notation(move.dest_coord)))
        if not move.is_capture and self._piece_at(move.dest_coord) is not NON:
            raise IllegalMoveException(str.format('{} is occupied', CoordinateParser.to_notation(move.dest_coord)))
        if move.piece_type == Pawn and not move.promotion_piece_type:
            if (move.player == 1 and move.dest_coord.row == 0) or (move.player == 2 and move.dest_coord.row == 7):
                raise IllegalMoveException('must promote on last rank')
        if move.promotion_piece_type:
            if move.piece_type != Pawn:
                raise IllegalMoveException('very sneaky')
            if move.promotion_piece_type in [Pawn, King]:
                raise IllegalMoveException('lol no')
            if (move.player == 1 and move.dest_coord.row != 0) or (move.player == 2 and move.dest_coord.row != 7):
                raise IllegalMoveException('very sneaky')
        # at this point we know that the move would be legal if there were a matching piece
        legal_piece_coordinate = self._find_piece_coord_with_legal_move(move)
        # we've found the piece matching this move, make the move
        self._commit_move(move.player, legal_piece_coordinate, move.dest_coord, move.promotion_piece_type, captures,
                          move_number)
        return (legal_piece_coordinate, move.dest_coord)

    def _commit_move(self, player, start_coord, dest_coord, promotion_piece_type, captures, move_number):
        '''
        Update the board state given a coordinate for a piece which we know can legally make this move.
        '''
        prev_board_array = self._copy_board_array()
        piece = self._piece_at(start_coord)
        # handle piece capture
        if self._piece_at(dest_coord) is not NON:
            captured_pawn = self._board_array[dest_coord.row][dest_coord.col]
            captures[player].append(captured_pawn)
        elif isinstance(piece, Pawn):
            maybe_enpassant_coord = self._maybe_get_enpassant_pawn_coord(player=player, coord=dest_coord,
                                                                         move_number=move_number)
            if maybe_enpassant_coord:
                captured_pawn = self._board_array[maybe_enpassant_coord.row][maybe_enpassant_coord.col]
                self._board_array[maybe_enpassant_coord.row][maybe_enpassant_coord.col] = NON
                captures[player].append(captured_pawn)
        # update the piece's new square
        if promotion_piece_type:
            self._board_array[dest_coord.row][dest_coord.col] = promotion_piece_type(player=player)
        else:
            self._board_array[dest_coord.row][dest_coord.col] = piece
        # clear the piece's previous square
        self._board_array[start_coord.row][start_coord.col] = NON

        # is the king in check in this new state? if yes revert
        if self.is_in_check(player):
            self._board_array = prev_board_array
            raise IllegalMoveException('move puts or leaves king in check')

        # set state for en passant
        if isinstance(piece, Pawn) and abs(start_coord.row - dest_coord.row) == 2:
            piece.can_enpassant_at_move_num = move_number
        if not piece.has_moved:
            piece.has_moved = True

    def _find_piece_coord_with_legal_move(self, move) -> Coordinate:
        '''
        find the coordinate for the piece that this move should apply to
        '''
        candidate_piece_coords = set()
        for coord in self._yield_coordinates():
            piece = self._piece_at(coord)
            if piece.player != move.player:
                continue
            if not isinstance(piece, move.piece_type):
                continue
            if move.start_col is not None and move.start_col != coord.col:
                continue
            if move.start_row is not None and move.start_row != coord.row:
                continue
            candidate_piece_coords.add(coord)
        if not candidate_piece_coords:
            raise IllegalMoveException(str.format('no {} to move', move.piece_type.__name__))

        legal_piece_coords = set()
        for candidate_piece_coord in candidate_piece_coords:
            if self._is_legal_move(move.player, candidate_piece_coord, move.dest_coord, move.is_capture):
                legal_piece_coords.add(candidate_piece_coord)
        if not legal_piece_coords:
            raise IllegalMoveException(str.format('{} is not a legal move', move.notation))
        if len(legal_piece_coords) > 1:
            example_coord = legal_piece_coords.pop()
            example_piece = self._piece_at(example_coord)
            example_notation = str.format('{}{}{}', example_piece.notation_char,
                                          CoordinateParser.to_notation(example_coord),
                                          CoordinateParser.to_notation(move.dest_coord))
            raise IllegalMoveException(
                str.format('multiple pieces match {}, use e.g. {}', move.notation, example_notation))
        return legal_piece_coords.pop()

    def _is_legal_move(self, player: int, start_coord: Coordinate, dest_coord: Coordinate, is_capture: bool):
        piece = self._piece_at(start_coord)
        if isinstance(piece, King):
            return self._is_legal_king_move(start_coord, dest_coord)
        if isinstance(piece, Rook):
            return self._is_legal_rook_move(start_coord, dest_coord)
        if isinstance(piece, Bishop):
            return self._is_legal_bishop_move(start_coord, dest_coord)
        if isinstance(piece, Queen):
            return self._is_legal_queen_move(start_coord, dest_coord)
        if isinstance(piece, Knight):
            return self._is_legal_knight_move(start_coord, dest_coord)
        if isinstance(piece, Pawn):
            return self._is_legal_pawn_move(player, start_coord, dest_coord, is_capture)
        return False

    def _is_legal_rook_move(self, start_coord, dest_coord):
        try:
            path_coords = start_coord.get_straight_path(dest_coord)
        except:
            return False
        return self._is_unobstructed(path_coords)

    def _is_legal_bishop_move(self, start_coord, dest_coord):
        try:
            path_coords = start_coord.get_diag_path(dest_coord)
        except:
            return False
        return self._is_unobstructed(path_coords)

    def _is_legal_queen_move(self, start_coord, dest_coord):
        try:
            path_coords = start_coord.get_straight_path(dest_coord)
        except:
            try:
                path_coords = start_coord.get_diag_path(dest_coord)
            except:
                return False
        return self._is_unobstructed(path_coords)

    def _is_legal_king_move(self, start_coord, dest_coord):
        return (abs(start_coord.row - dest_coord.row) <= 1 and abs(
            start_coord.col - dest_coord.col) <= 1)

    def _is_legal_knight_move(self, start_coord, dest_coord):
        return (abs(start_coord.row - dest_coord.row) == 2 and abs(
            start_coord.col - dest_coord.col) == 1) or (
                       abs(start_coord.row - dest_coord.row) == 1 and abs(
                   start_coord.col - dest_coord.col) == 2)

    def _is_legal_pawn_move(self, player, start_coord, dest_coord, is_capture):
        if not is_capture:
            return self._is_legal_pawn_push(player, start_coord, dest_coord)
        else:
            return self._is_legal_pawn_capture(player, start_coord, dest_coord)

    def _is_legal_pawn_push(self, player: int, start_coord: Coordinate, dest_coord: Coordinate):
        if start_coord.col != dest_coord.col:
            return False
        # allow 2 sq distance on first move, else 1
        move_distance = abs(start_coord.row - dest_coord.row)
        max_move = 1 if self._piece_at(start_coord).has_moved else 2
        if move_distance > max_move:
            return False
        # assert that pawn is moving forward
        if player == 1 and start_coord.row - dest_coord.row < 0:
            return False
        if player == 2 and start_coord.row - dest_coord.row > 0:
            return False
        return True

    def _is_legal_pawn_capture(self, player: int, start_coord: Coordinate, dest_coord: Coordinate):
        if player == 1:
            return dest_coord.row == start_coord.row - 1 and (
                    dest_coord.col == start_coord.col - 1 or dest_coord.col == start_coord.col + 1)
        if player == 2:
            return dest_coord.row == start_coord.row + 1 and (
                    dest_coord.col == start_coord.col - 1 or dest_coord.col == start_coord.col + 1)

    def _maybe_get_enpassant_pawn_coord(self, player, coord: Coordinate, move_number: int):
        if player == 1:
            if coord.row != 2:
                return None
            maybe_enpassant_pawn_coord = Coordinate(row=coord.row + 1, col=coord.col)
        elif player == 2:
            if coord.row != 5:
                return None
            maybe_enpassant_pawn_coord = Coordinate(row=coord.row - 1, col=coord.col)
        else:
            raise SystemError()
        if not isinstance(self._piece_at(maybe_enpassant_pawn_coord), Pawn):
            return None
        if self._piece_at(maybe_enpassant_pawn_coord).can_enpassant_at_move_num == move_number - 1:
            return maybe_enpassant_pawn_coord
        else:
            return None

    def _get_king_coord(self, player):
        for coord in self._yield_coordinates():
            piece = self._piece_at(coord)
            if piece.player == player and isinstance(piece, King):
                return coord
        raise SystemError(str.format('no king for p{}', player))

    def _yield_coordinates(self):
        for r in range(len(self._board_array)):
            for c in range(len(self._board_array[r])):
                yield Coordinate(row=r, col=c)

    def _piece_at(self, coord) -> Piece:
        return self._board_array[coord.row][coord.col]

    def _is_unobstructed(self, path_coords):
        for coord in path_coords:
            if self._piece_at(coord) is not NON:
                return False
        return True

    def _does_player_target(self, player, coords_to_check: List[Coordinate]):
        for coord in self._yield_coordinates():
            piece = self._piece_at(coord)
            if piece.player != player or piece is NON:
                continue
            for coord_to_check in coords_to_check:
                if self._does_player_piece_target(player, piece_coord=coord, dest_coord=coord_to_check):
                    return True
        return False

    def _does_player_piece_target(self, player, piece_coord: Coordinate, dest_coord: Coordinate) -> bool:
        piece = self._piece_at(piece_coord)
        if piece is NON:
            return False
        if isinstance(piece, King):
            return self._is_legal_king_move(piece_coord, dest_coord)
        if isinstance(piece, Rook):
            return self._is_legal_rook_move(piece_coord, dest_coord)
        if isinstance(piece, Bishop):
            return self._is_legal_bishop_move(piece_coord, dest_coord)
        if isinstance(piece, Queen):
            return self._is_legal_queen_move(piece_coord, dest_coord)
        if isinstance(piece, Knight):
            return self._is_legal_knight_move(piece_coord, dest_coord)
        if isinstance(piece, Pawn):
            return self._is_legal_pawn_capture(player, piece_coord, dest_coord)
