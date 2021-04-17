class Piece:
    def __init__(self, solid_char, empty_char, player, notation_char, piece_value):
        self.char = solid_char
        self.player = player
        self.notation_char = notation_char
        self.piece_value = piece_value
        self.empty_char = empty_char
        self.has_moved = False


class Pawn(Piece):
    def __init__(self, player):
        super().__init__('o', 'p', player, 'P', 1)
        self.can_enpassant_at_move_num = -1


class Rook(Piece):
    def __init__(self, player):
        super().__init__('t', 'r', player, 'R', 5)


class Knight(Piece):
    def __init__(self, player):
        super().__init__('m', 'n', player, 'N', 3)


class Bishop(Piece):
    def __init__(self, player):
        super().__init__('v', 'b', player, 'B', 3)


class King(Piece):
    def __init__(self, player):
        super().__init__('l', 'k', player, 'K', 100)


class Queen(Piece):
    def __init__(self, player):
        super().__init__('w', 'q', player, 'Q', 9)


class Empty(Piece):
    def __init__(self):
        super().__init__(' ', ' ', None, '', 0)


NOTATION_TO_PIECE_TYPE = {'R': Rook, 'N': Knight, 'B': Bishop, 'Q': Queen, 'K': King}
PIECE_TYPE_TO_NOTATION = {Rook: 'R', Knight: 'N', Bishop: 'B', Queen: 'Q', King: 'K'}


def R_B():
    return Rook(player=2)


def R_W():
    return Rook(player=1)


def N_B():
    return Knight(player=2)


def N_W():
    return Knight(player=1)


def B_B():
    return Bishop(player=2)


def B_W():
    return Bishop(player=1)


def K_B():
    return King(player=2)


def K_W():
    return King(player=1)


def Q_B():
    return Queen(player=2)


def Q_W():
    return Queen(player=1)


def P_B():
    return Pawn(player=2)


def P_W():
    return Pawn(player=1)
