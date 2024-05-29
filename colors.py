from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
    ORANGE = 4
    TEAL = 5
    PURPLE = 6
    MAGENTA = 7
    GRAY = 8

# TODO
COLOR_TO_TUPLE = {
    Color.RED: (230, 128, 105),
    Color.GREEN: (193, 221, 168),
    Color.BLUE: (166, 189, 249),
    Color.ORANGE: (238, 203, 154),
    Color.TEAL: (178, 209, 214),
    Color.PURPLE: (182, 166, 221),
    Color.MAGENTA: (203, 163, 187),
    Color.GRAY: (224, 224, 224)
}