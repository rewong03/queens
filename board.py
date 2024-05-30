from tile import Tile, TileState
from colors import Color, COLOR_TO_TUPLE
from constants import GRID_SIZE, MIN_COLOR_SIZE_COUNTS
from generate_queens import generate_random_board_posns

import random
import time

class Board:
    def __init__(self):
        self._board = [[None for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
        self.queen_posns = set()
        self.color_groups = {}
        self.color_queen_count = [0 for _ in range(len(Color))]

        for i in range(1, len(Color) + 1):
            self.color_groups[Color(i)] = set()

    def __repr__(self):
        string = "board = Board()\n"
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                string += f"board.set_tile(({i}, {j}), {repr(self._board[i][j])})" + "\n"

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
        if any(board._board[row][i].state == TileState.QUEEN for i in range(col)):
            return False
        # for i in range(col):
        #     if board._board[row][i].state == TileState.QUEEN:
        #         # print(f"{posn} left row {(row, i)}")
        #         return False
    
        # Check upper diagonal on left side
        for i, j in zip(range(row, max(row - 2, -1), -1), range(col, max(col - 2, -1), -1)):
            # print(f"Compare {posn} {(i, j)}")
            if board._board[i][j].state == TileState.QUEEN:
                # print(f"{posn} left upper dag {i, j}")
                return False
    
        # Check lower diagonal on left side
        for i, j in zip(range(row, min(row + 2, GRID_SIZE), 1), range(col, max(col - 2, -1), -1)):
            if board._board[i][j].state == TileState.QUEEN:
                # print(f"{posn} left lower diag {i, j}")
                return False
            
        return board.color_queen_count[board.get_tile(posn).color.value - 1] == 0
        # return True

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

    @staticmethod
    # @profile
    def color_board(board):
        color_frontier = []

        # color the queens
        available_colors = list(COLOR_TO_TUPLE.keys())
        for i, j in board.queen_posns:
            tile = board.get_tile((i, j))
            color = random.choice(available_colors)

            tile.color = color
            available_colors.remove(color)

            color_frontier.append((color, {(i, j)}))
            board.color_groups[color].add(tile)

        # constrain coloring
        queen_posns = list(board.queen_posns)
        size_constraints = {Color(i): 0 for i in range(1, len(Color) + 1)}
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

            # max_idx = color_frontier.index(max(color_frontier))
            # color_frontier[0], color_frontier[max_idx] = color_frontier[max_idx], color_frontier[0]

            color_frontier.sort(reverse=True, key=lambda x: size_constraints[x[0]])
            if size_constraints[color_frontier[0][0]] <= 0:
                random.shuffle(color_frontier)
            # print(color_frontier)
            # print(size_constraints)
            # input()
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

                    if size_constraints[color] > 0:
                        return False

                    continue

                percent_colored = len(board.color_groups[color]) / (GRID_SIZE ** 2)
                percent_do_nothing = 1 - (1 - percent_colored) ** 3

                if size_constraints[color] > 0:
                    # print("HERE")
                    percent_do_nothing = 0

                if random.uniform(0, 1) < percent_do_nothing:
                    # print(color, " HERE")
                    posns.add((i, j))
                else:
                    posn_to_color = random.choice(possible_tiles_to_color)
                    tile_to_color = board.get_tile(posn_to_color)
                    tile_to_color.color = color
                    board.color_groups[color].add(tile_to_color)
                    uncolored_tiles.remove(posn_to_color)
                    size_constraints[color] -= 1

                    # print(color)

                    posns.add(posn_to_color)

                # there are other neighbors of (i, j) that are uncolored
                if len(possible_tiles_to_color) > 1:
                    posns.add((i, j))

                if not posns:
                    colors_to_remove.add(color)
                    

                if size_constraints[color] > 0:
                    # print("BRUH")
                    break

            color_frontier = [x for x in color_frontier if x[0] not in colors_to_remove]
                

        return len(uncolored_tiles) == 0
    
    @staticmethod
    # @profile
    def has_multiple_solutions(board, col=0):
        """This function returns a number. It pre-emptively stops when it has more than one 
        solution and just returns the number of solutions found at the stop"""
        if col >= GRID_SIZE:
            # queen_posns = set()
            # for i in range(GRID_SIZE):
            #     for j in range(GRID_SIZE):
            #         if board.get_tile((i, j)).state == TileState.QUEEN:
            #             queen_posns.add((i, j))

            # print(queen_posns)
            return board.is_solved()
        
        num_solutions = 0
        for i in range(GRID_SIZE):
            if Board._is_valid_queen_posn(board, (i, col)):
                # print(f"Queening {(i, col)}")
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
                            board.set_tile((i, j), Tile(i, j, None, True, TileState.EMPTY))
                        else:
                            board.set_tile((i, j), Tile(i, j, None, False, TileState.EMPTY))

            
            colored_board = board.copy()
            if Board.color_board(colored_board):
                # break
                sols = Board.has_multiple_solutions(colored_board)
                # print(sols)
                if sols == 1:
                    print(f"Took {iters} iters {time.time() - t0} seconds")
                    return colored_board
                # break

            print(iters)
            iters += 1
            # if i > 25:
            #     break
            # colored_board = board.copy()

        # print(Board.find_num_solutions(colored_board))
        print(f"Took {i} iters")
        return colored_board

        # board = Board()
        # board.set_tile((0, 0), Tile(0, 0, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((0, 1), Tile(0, 1, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((0, 2), Tile(0, 2, Color.MAGENTA, True, TileState.EMPTY))
        # board.set_tile((0, 3), Tile(0, 3, Color.BLUE, False, TileState.EMPTY))
        # board.set_tile((0, 4), Tile(0, 4, Color.BLUE, False, TileState.EMPTY))
        # board.set_tile((0, 5), Tile(0, 5, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((0, 6), Tile(0, 6, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((0, 7), Tile(0, 7, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((1, 0), Tile(1, 0, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((1, 1), Tile(1, 1, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((1, 2), Tile(1, 2, Color.MAGENTA, False, TileState.EMPTY))
        # board.set_tile((1, 3), Tile(1, 3, Color.MAGENTA, False, TileState.EMPTY))
        # board.set_tile((1, 4), Tile(1, 4, Color.BLUE, False, TileState.EMPTY))
        # board.set_tile((1, 5), Tile(1, 5, Color.BLUE, True, TileState.EMPTY))
        # board.set_tile((1, 6), Tile(1, 6, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((1, 7), Tile(1, 7, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((2, 0), Tile(2, 0, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((2, 1), Tile(2, 1, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((2, 2), Tile(2, 2, Color.GRAY, False, TileState.EMPTY))
        # board.set_tile((2, 3), Tile(2, 3, Color.BLUE, False, TileState.EMPTY))
        # board.set_tile((2, 4), Tile(2, 4, Color.BLUE, False, TileState.EMPTY))
        # board.set_tile((2, 5), Tile(2, 5, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((2, 6), Tile(2, 6, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((2, 7), Tile(2, 7, Color.TEAL, True, TileState.EMPTY))
        # board.set_tile((3, 0), Tile(3, 0, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((3, 1), Tile(3, 1, Color.GRAY, True, TileState.EMPTY))
        # board.set_tile((3, 2), Tile(3, 2, Color.GRAY, False, TileState.EMPTY))
        # board.set_tile((3, 3), Tile(3, 3, Color.RED, False, TileState.EMPTY))
        # board.set_tile((3, 4), Tile(3, 4, Color.RED, False, TileState.EMPTY))
        # board.set_tile((3, 5), Tile(3, 5, Color.RED, False, TileState.EMPTY))
        # board.set_tile((3, 6), Tile(3, 6, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((3, 7), Tile(3, 7, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((4, 0), Tile(4, 0, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((4, 1), Tile(4, 1, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((4, 2), Tile(4, 2, Color.RED, False, TileState.EMPTY))
        # board.set_tile((4, 3), Tile(4, 3, Color.RED, True, TileState.EMPTY))
        # board.set_tile((4, 4), Tile(4, 4, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((4, 5), Tile(4, 5, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((4, 6), Tile(4, 6, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((4, 7), Tile(4, 7, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((5, 0), Tile(5, 0, Color.PURPLE, True, TileState.EMPTY))
        # board.set_tile((5, 1), Tile(5, 1, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((5, 2), Tile(5, 2, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((5, 3), Tile(5, 3, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((5, 4), Tile(5, 4, Color.GREEN, False, TileState.EMPTY))
        # board.set_tile((5, 5), Tile(5, 5, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((5, 6), Tile(5, 6, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((5, 7), Tile(5, 7, Color.TEAL, False, TileState.EMPTY))
        # board.set_tile((6, 0), Tile(6, 0, Color.PURPLE, False, TileState.EMPTY))
        # board.set_tile((6, 1), Tile(6, 1, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((6, 2), Tile(6, 2, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((6, 3), Tile(6, 3, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((6, 4), Tile(6, 4, Color.GREEN, True, TileState.EMPTY))
        # board.set_tile((6, 5), Tile(6, 5, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((6, 6), Tile(6, 6, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((6, 7), Tile(6, 7, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((7, 0), Tile(7, 0, Color.PURPLE, False, TileState.EMPTY))
        # board.set_tile((7, 1), Tile(7, 1, Color.PURPLE, False, TileState.EMPTY))
        # board.set_tile((7, 2), Tile(7, 2, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((7, 3), Tile(7, 3, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((7, 4), Tile(7, 4, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((7, 5), Tile(7, 5, Color.ORANGE, False, TileState.EMPTY))
        # board.set_tile((7, 6), Tile(7, 6, Color.ORANGE, True, TileState.EMPTY))
        # board.set_tile((7, 7), Tile(7, 7, Color.ORANGE, False, TileState.EMPTY))

        # for i, j in {(4, 4), (2, 1), (6, 5), (0, 0), (5, 7), (7, 6), (3, 2), (1, 3)}:
        #     board.get_tile((i, j)).state = TileState.QUEEN
        # return board
    
if __name__ == "__main__":
    board = Board.generate_random_board()
    # print(board)

    # board = Board()
    # board.set_tile((0, 0), Tile(0, 0, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((0, 1), Tile(0, 1, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((0, 2), Tile(0, 2, Color.MAGENTA, True, TileState.EMPTY))
    # board.set_tile((0, 3), Tile(0, 3, Color.BLUE, False, TileState.EMPTY))
    # board.set_tile((0, 4), Tile(0, 4, Color.BLUE, False, TileState.EMPTY))
    # board.set_tile((0, 5), Tile(0, 5, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((0, 6), Tile(0, 6, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((0, 7), Tile(0, 7, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((1, 0), Tile(1, 0, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((1, 1), Tile(1, 1, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((1, 2), Tile(1, 2, Color.MAGENTA, False, TileState.EMPTY))
    # board.set_tile((1, 3), Tile(1, 3, Color.MAGENTA, False, TileState.EMPTY))
    # board.set_tile((1, 4), Tile(1, 4, Color.BLUE, False, TileState.EMPTY))
    # board.set_tile((1, 5), Tile(1, 5, Color.BLUE, True, TileState.EMPTY))
    # board.set_tile((1, 6), Tile(1, 6, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((1, 7), Tile(1, 7, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((2, 0), Tile(2, 0, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((2, 1), Tile(2, 1, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((2, 2), Tile(2, 2, Color.GRAY, False, TileState.EMPTY))
    # board.set_tile((2, 3), Tile(2, 3, Color.BLUE, False, TileState.EMPTY))
    # board.set_tile((2, 4), Tile(2, 4, Color.BLUE, False, TileState.EMPTY))
    # board.set_tile((2, 5), Tile(2, 5, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((2, 6), Tile(2, 6, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((2, 7), Tile(2, 7, Color.TEAL, True, TileState.EMPTY))
    # board.set_tile((3, 0), Tile(3, 0, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((3, 1), Tile(3, 1, Color.GRAY, True, TileState.EMPTY))
    # board.set_tile((3, 2), Tile(3, 2, Color.GRAY, False, TileState.EMPTY))
    # board.set_tile((3, 3), Tile(3, 3, Color.RED, False, TileState.EMPTY))
    # board.set_tile((3, 4), Tile(3, 4, Color.RED, False, TileState.EMPTY))
    # board.set_tile((3, 5), Tile(3, 5, Color.RED, False, TileState.EMPTY))
    # board.set_tile((3, 6), Tile(3, 6, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((3, 7), Tile(3, 7, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((4, 0), Tile(4, 0, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((4, 1), Tile(4, 1, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((4, 2), Tile(4, 2, Color.RED, False, TileState.EMPTY))
    # board.set_tile((4, 3), Tile(4, 3, Color.RED, True, TileState.EMPTY))
    # board.set_tile((4, 4), Tile(4, 4, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((4, 5), Tile(4, 5, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((4, 6), Tile(4, 6, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((4, 7), Tile(4, 7, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((5, 0), Tile(5, 0, Color.PURPLE, True, TileState.EMPTY))
    # board.set_tile((5, 1), Tile(5, 1, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((5, 2), Tile(5, 2, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((5, 3), Tile(5, 3, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((5, 4), Tile(5, 4, Color.GREEN, False, TileState.EMPTY))
    # board.set_tile((5, 5), Tile(5, 5, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((5, 6), Tile(5, 6, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((5, 7), Tile(5, 7, Color.TEAL, False, TileState.EMPTY))
    # board.set_tile((6, 0), Tile(6, 0, Color.PURPLE, False, TileState.EMPTY))
    # board.set_tile((6, 1), Tile(6, 1, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((6, 2), Tile(6, 2, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((6, 3), Tile(6, 3, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((6, 4), Tile(6, 4, Color.GREEN, True, TileState.EMPTY))
    # board.set_tile((6, 5), Tile(6, 5, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((6, 6), Tile(6, 6, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((6, 7), Tile(6, 7, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((7, 0), Tile(7, 0, Color.PURPLE, False, TileState.EMPTY))
    # board.set_tile((7, 1), Tile(7, 1, Color.PURPLE, False, TileState.EMPTY))
    # board.set_tile((7, 2), Tile(7, 2, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((7, 3), Tile(7, 3, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((7, 4), Tile(7, 4, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((7, 5), Tile(7, 5, Color.ORANGE, False, TileState.EMPTY))
    # board.set_tile((7, 6), Tile(7, 6, Color.ORANGE, True, TileState.EMPTY))
    # board.set_tile((7, 7), Tile(7, 7, Color.ORANGE, False, TileState.EMPTY))

    # print(Board.has_multiple_solutions(board))