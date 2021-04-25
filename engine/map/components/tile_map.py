from config import Config
from engine.map.components.coordinate import Coordinate
from engine.map.components.tile import Tile


class TileGenerator:

    def refresh_tiles(self, board_array):
        self._tile_grid = self._get_tile_grid(board_array)

    def get_tiles(self):
        for row in range(len(self._tile_grid)):
            for col in range(len(self._tile_grid[0])):
                yield self._tile_grid[row][col]

    def get_tile_at(self, coord: Coordinate):
        return self._tile_grid[coord.row][coord.col]

    def _get_tile_grid(self, board_array):
        tile_grid = []
        is_dark_square = False
        for r in range(len(board_array)):
            tile_grid.append([])
            for c in range(len(board_array[r])):
                piece = board_array[r][c]
                tile_grid[r].append(Tile(coordinate=Coordinate(row=r, col=c),
                                         bg_color=Config.DARK_SQ_COLOR if is_dark_square else Config.LIGHT_SQ_COLOR,
                                         char=piece.char,
                                         char_color=Config.WHITE_PIECE_COLOR if piece.player == 1 else Config.BLACK_PIECE_COLOR))
                is_dark_square = not is_dark_square
            is_dark_square = not is_dark_square
        return tile_grid
