from colors import Color
from enum import Enum
import random
import math

class TileState(Enum):
    EMPTY = 0
    MARKED = 1
    QUEEN = 2
    QUESTION = 4

class Tile:
    def __init__(self, x: int, y: int, color: Color, is_queen: bool, state: TileState):
        # x and y is the position of the tile
        # color is the color of the tile
        # is_queen is whether there's a queen on this tile (ground truth)
        # state is the user state of the tile

        self.x = x
        self.y = y
        self.color = color
        self.is_queen = is_queen
        self.state = state

        self.animation_tick = random.randint(0, 500)

    def get_next_scale_factor(self):
        self.animation_tick += 1
        return math.sin(self.animation_tick / 25) * 0.3 + 0.7
    
    def copy(self):
        return Tile(self.x, self.y, self.color, self.is_queen, self.state)