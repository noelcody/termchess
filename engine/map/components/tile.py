from engine.map.components.coordinate import Coordinate


class Tile:
    def __init__(self, coordinate: Coordinate, bg_color, char, char_color):
        self.coordinate = coordinate
        self.bg_color = bg_color
        self.char = char if char else ' '
        self.char_color = char_color
