from tile import Tile, TileState
from colors import Color, COLOR_TO_TUPLE
from constants import GRID_SIZE, COLOR_SIZE_COUNTS
from generate_queens import generate_random_board_posns

import random

class Board:
    def __init__(self):
        self._board = [[None for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
        self.queen_posns = set()
        self.color_groups = {}

        for i in range(1, len(Color) + 1):
            self.color_groups[Color(i)] = set()

    def get_tile(self, posn):
        x, y = posn

        if x < 0 or x > GRID_SIZE or y < 0 or y > GRID_SIZE:
            raise ValueError(f"Tried to access board out of bounds (position ({x}, {y}))")
        
        tile = self._board[x][y]
        if tile:
            return tile
        
        raise ValueError(f"Tried to access a tile that hasn't been set (position ({x}, {y}))")
    
    def set_tile(self, posn, tile):
        x, y = posn

        if x < 0 or x > GRID_SIZE or y < 0 or y > GRID_SIZE:
            raise ValueError(f"Tried to set board out of bounds (position ({x}, {y}))")
        
        if tile.is_queen:
            self.queen_posns.add((x, y))
        elif self._board[x][y] and self._board[x][y].is_queen:
            self.queen_posns.remove((x, y))
        
        self._board[x][y] = tile

    def _is_valid_queen_posn(self, posn):
        row, col = posn

        # Check this row on left side
        for i in range(col):
            if self.get_tile((row, i)).state == TileState.QUEEN:
                print(f"{posn} left row {(row, i)}")
                return False
    
        # Check upper diagonal on left side
        for i, j in zip(range(row, max(row - 2, -1), -1), range(col, max(row - 2, -1), -1)):
            if self.get_tile((i, j)).state == TileState.QUEEN:
                print(f"{posn} left upper dag {i, j}")
                return False
    
        # Check lower diagonal on left side
        for i, j in zip(range(row, min(row + 2, GRID_SIZE), 1), range(col, max(col - 2, -1), -1)):
            if self.get_tile((i, j)).state == TileState.QUEEN:
                print(f"{posn} left lower diag {i, j}")
                return False
    
        return True

    def is_solved(self):
        if all(self.get_tile((i, j)).state == TileState.QUEEN for i, j in self.queen_posns):
            return True
        
        colors_with_queens = set()
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                tile = self.get_tile((i, j))
                if tile.state == TileState.QUEEN:
                    tile.state = TileState.EMPTY
                    is_valid = self._is_valid_queen_posn((i, j))
                    tile.state = TileState.QUEEN

                    if not is_valid:
                        return False
                    
                    colors_with_queens.add(tile.color)
                    
        return len(colors_with_queens) == len(Color)


    @staticmethod
    def color_board(board):
        color_frontier = []

        # color the queens
        available_colors = list(COLOR_TO_TUPLE.keys())
        for (i, j) in board.queen_posns:
            tile = board.get_tile((i, j))
            color = random.choice(available_colors)

            tile.color = color
            print(tile.x, tile.y, color)
            available_colors.remove(color)

            color_frontier.append((i, j))
            board.color_groups[color].add(tile)

        # constrain coloring
        queen_posns = list(board.queen_posns)
        size_constraints = {Color(i): GRID_SIZE ** 2 for i in range(1, len(Color) + 1)}
        for color_size, color_count in COLOR_SIZE_COUNTS.items():
            for _ in range(color_count):
                queen_posn = random.choice(queen_posns)
                queen_tile = board.get_tile(queen_posn)

                # subtract 1 because we colored the queen
                size_constraints[queen_tile.color] = color_size - 1
                queen_posns.remove(queen_posn)

        print(size_constraints)

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
            # print(size_constraints)
            # print(f"Uncolored: {len(uncolored_tiles)}")
            # print(f"Frontier: {len(color_frontier)}")
            # input()
            new_color_frontier = []
            # for (i, j) in sorted(color_frontier, key=lambda x: size_constraints[board.get_tile(x).color]):
            random.shuffle(color_frontier)
            for (i, j) in color_frontier:
                color = board.get_tile((i, j)).color
                possible_tiles_to_color = [posn for posn in get_neighbors(i, j) if posn in uncolored_tiles]

                if not possible_tiles_to_color:
                    continue

                if size_constraints[color] <= 0:
                    continue

                # 30% chance of doing nothing
                if random.randint(1, 10) <= 3:
                    new_color_frontier.append((i, j))
                else:
                    posn_to_color = random.choice(possible_tiles_to_color)
                    tile_to_color = board.get_tile(posn_to_color)
                    tile_to_color.color = color
                    board.color_groups[color].add(tile_to_color)
                    uncolored_tiles.remove(posn_to_color)
                    size_constraints[color] -= 1

                    new_color_frontier.append(posn_to_color)
                
                # there are other neighbord of (i, j) that are uncolored
                if len(possible_tiles_to_color) > 1:
                    new_color_frontier.append((i, j))
            
            color_frontier = new_color_frontier

        return len(uncolored_tiles) == 0
    
    def copy(self):
        board = Board()

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                board.set_tile((i, j), self.get_tile((i, j)).copy())

        return board

    @staticmethod
    def generate_random_board():
        board = Board()
        queen_posns = set(generate_random_board_posns())

        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if (i, j) in queen_posns:
                    board.set_tile((i, j), Tile(i, j, None, True, TileState.EMPTY))
                else:
                    board.set_tile((i, j), Tile(i, j, None, False, TileState.EMPTY))

        colored_board = board.copy()
        while not Board.color_board(colored_board):
            colored_board = board.copy()

        return colored_board
