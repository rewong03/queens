from tile import Tile, TileState
from colors import Color, COLOR_TO_TUPLE
from constants import GRID_SIZE, MIN_COLOR_SIZE_COUNTS
from generate_queens import generate_random_board_posns, is_safe

import random
import time
from math import atan2, pi


class Board:
    def __init__(self):
        self._board = [[None for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
        self.queen_posns = set()
        self.color_groups = {}

        # for more efficient board generation
        self.color_queen_count = [0 for _ in range(len(Color))]
        self.row_queen_count = [0 for _ in range(GRID_SIZE)]

        for i in range(1, len(Color) + 1):
            self.color_groups[Color(i)] = set()

    def __repr__(self):
        string = "board = Board()\n"
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                string += (
                    f"board.set_tile(({i}, {j}), {repr(self._board[i][j])})" + "\n"
                )

        return string

    def get_tile(self, posn):
        x, y = posn

        if x < 0 or x > GRID_SIZE or y < 0 or y > GRID_SIZE:
            raise ValueError(
                f"Tried to access board out of bounds (position ({x}, {y}))"
            )

        tile = self._board[x][y]
        if tile:
            return tile

        raise ValueError(
            f"Tried to access a tile that hasn't been set (position ({x}, {y}))"
        )

    def set_tile(self, posn, tile):
        x, y = posn

        if x < 0 or x > GRID_SIZE or y < 0 or y > GRID_SIZE:
            raise ValueError(f"Tried to set board out of bounds (position ({x}, {y}))")

        if tile.is_queen:
            self.queen_posns.add((x, y))
        elif self._board[x][y] and self._board[x][y].is_queen:
            self.queen_posns.remove((x, y))

        tile.board = self
        self._board[x][y] = tile

    @staticmethod
    # @profile
    def _is_valid_queen_posn(board, posn):
        row, col = posn

        # Check this row on left side
        if board.row_queen_count[row] > 0:
            return False

        # Check upper diagonal on left side
        if board._board[max(row - 1, 0)][max(col - 1, 0)].state == TileState.QUEEN:
            return False

        # Check lower diagonal on left side
        if (
            board._board[min(row + 1, GRID_SIZE - 1)][max(col - 1, 0)]
            == TileState.QUEEN
        ):
            return False

        return board.color_queen_count[board.get_tile(posn).color.value - 1] == 0

    # @profile
    def is_solved(self):
        if all(
            self.get_tile((i, j)).state == TileState.QUEEN for i, j in self.queen_posns
        ):
            return True

        queen_count = 0
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                tile = self.get_tile((i, j))
                if tile.state == TileState.QUEEN:
                    queen_count += 1

                    tile.state = TileState.EMPTY
                    is_valid = Board._is_valid_queen_posn(self, (i, j))
                    tile.state = TileState.QUEEN

                    if not is_valid:
                        return False

        return queen_count == GRID_SIZE

    def copy(self):
        board = Board()

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                board.set_tile((i, j), self.get_tile((i, j)).copy())

        return board

    def clear_colors(self):
        """All tile states must be EMPTY before calling this"""
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self._board[i][j].color = None

        self.color_queen_count = [0 for _ in range(len(Color))]

        for i in range(1, len(Color) + 1):
            self.color_groups[Color(i)] = set()

    def to_dict(self):
        board_dict = []
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                board_dict.append(self._board[i][j].to_dict())

        return board_dict

    def set_up_win_animation(self):
        centroid_x, centroid_y = GRID_SIZE / 2, GRID_SIZE / 2

        angles = []
        for i, j in self.queen_posns:
            tile = self._board[i][j]
            angles.append(
                (
                    atan2(tile.y - centroid_y, tile.x - centroid_x),
                    (tile.y - centroid_y) ** 2 + (tile.x - centroid_x) ** 2,
                    tile,
                )
            )

        angles.sort()
        for i in range(len(angles)):
            _, _, tile = angles[i]
            tile.set_animation_function(0.3, 2 * pi / 50, i * 2 * pi / len(angles), 0.7)

    @staticmethod
    def from_dict(d):
        board = Board()

        for tile_d in d:
            tile = Tile.from_dict(tile_d)
            board.set_tile((tile.x, tile.y), tile)

        return board

    @staticmethod
    # @profile
    def color_board(board):
        color_frontier = []

        # randomly color the queens
        available_colors = list(COLOR_TO_TUPLE.keys())
        for i, j in board.queen_posns:
            tile = board.get_tile((i, j))
            color = random.choice(available_colors)

            tile.color = color
            available_colors.remove(color)

            # add tile into frontier, we will try to color the neighbors
            color_frontier.append((color, {(i, j)}))
            board.color_groups[color].add(tile)

        # mapping of colors and the number of tiles that must have that color
        size_constraints = {Color(i): 0 for i in range(1, len(Color) + 1)}
        queen_posns = list(board.queen_posns)
        for color_size, color_count in MIN_COLOR_SIZE_COUNTS.items():
            for _ in range(color_count):
                queen_posn = random.choice(queen_posns)
                queen_tile = board.get_tile(queen_posn)

                # subtract 1 because we colored the queen
                size_constraints[queen_tile.color] = color_size - 1
                queen_posns.remove(queen_posn)

        uncolored_tiles = set()
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if not board.get_tile((i, j)).color:
                    uncolored_tiles.add((i, j))

        def posn_in_bounds(i, j):
            return i >= 0 and i < GRID_SIZE and j >= 0 and j < GRID_SIZE

        def get_neighbors(i, j):
            neighbors = []

            if posn_in_bounds(i + 1, j):
                neighbors.append((i + 1, j))

            if posn_in_bounds(i - 1, j):
                neighbors.append((i - 1, j))

            if posn_in_bounds(i, j + 1):
                neighbors.append((i, j + 1))

            if posn_in_bounds(i, j - 1):
                neighbors.append((i, j - 1))

            return neighbors

        while uncolored_tiles and len(color_frontier) > 0:
            colors_to_remove = set()

            # try to satisfy the largest remaining constraint
            color_frontier.sort(reverse=True, key=lambda x: size_constraints[x[0]])
            if size_constraints[color_frontier[0][0]] <= 0:
                random.shuffle(color_frontier)

            for color, posns in color_frontier:
                if not posns:
                    continue

                posn = random.choice(tuple(posns))
                posns.remove(posn)
                i, j = posn

                possible_tiles_to_color = [
                    posn for posn in get_neighbors(i, j) if posn in uncolored_tiles
                ]

                if not possible_tiles_to_color:
                    if not posns:
                        colors_to_remove.add(color)

                    # early stop if we can't satisfy constraints
                    if size_constraints[color] > 0:
                        return False

                    continue

                # decide whether to color a tile, randomly weighted by number of tiles with that color
                percent_colored = len(board.color_groups[color]) / (GRID_SIZE**2)
                percent_do_nothing = 1 - (1 - percent_colored) ** 3

                if size_constraints[color] > 0:
                    percent_do_nothing = 0

                if random.uniform(0, 1) < percent_do_nothing:
                    posns.add((i, j))
                else:
                    posn_to_color = random.choice(possible_tiles_to_color)
                    tile_to_color = board.get_tile(posn_to_color)
                    tile_to_color.color = color
                    board.color_groups[color].add(tile_to_color)
                    uncolored_tiles.remove(posn_to_color)
                    size_constraints[color] -= 1

                    posns.add(posn_to_color)

                # there are other neighbors of (i, j) that are uncolored
                if len(possible_tiles_to_color) > 1:
                    posns.add((i, j))

                if not posns:
                    colors_to_remove.add(color)

                if size_constraints[color] > 0:
                    break

            color_frontier = [x for x in color_frontier if x[0] not in colors_to_remove]

        return len(uncolored_tiles) == 0

    @staticmethod
    # @profile
    def has_multiple_solutions(board, col=0):
        """This function returns a number. It pre-emptively stops when it has more than one
        solution and just returns the number of solutions found at the stop"""
        if col >= GRID_SIZE:
            return board.is_solved()

        num_solutions = 0
        for i in range(GRID_SIZE):
            if Board._is_valid_queen_posn(board, (i, col)):
                board.get_tile((i, col)).state = TileState.QUEEN
                num_solutions += Board.has_multiple_solutions(board, col + 1)
                board.get_tile((i, col)).state = TileState.EMPTY

            if num_solutions > 1:
                return num_solutions

        return num_solutions

    @staticmethod
    # @profile
    def generate_random_board():
        iters = 0
        board = Board()
        t0 = time.time()
        while True:
            if iters % 10 == 0:
                board = Board()
                queen_posns = set(generate_random_board_posns())

                for i in range(GRID_SIZE):
                    for j in range(GRID_SIZE):
                        if (i, j) in queen_posns:
                            board.set_tile(
                                (i, j), Tile(i, j, None, True, TileState.EMPTY)
                            )
                        else:
                            board.set_tile(
                                (i, j), Tile(i, j, None, False, TileState.EMPTY)
                            )

            board.clear_colors()
            if Board.color_board(board):
                sols = Board.has_multiple_solutions(board)
                if sols == 1:
                    print(f"Took {iters} iters {time.time() - t0} seconds")
                    return board

            iters += 1


if __name__ == "__main__":
    import json

    board = Board.generate_random_board()
    json.dumps(board.to_dict())
    board.set_up_win_animation()
