# helper functions for randomly generating a board that satisfies the N-queens problem
# https://www.geeksforgeeks.org/python-program-for-n-queen-problem-backtracking-3/

from constants import GRID_SIZE
import random


def copy_board(board):
    return [row.copy() for row in board]


def print_board(board):
    for row in board:
        print(" ".join(map(str, row)))


def is_safe(board, row, col):
    # Check this row on left side
    for i in range(col):
        if board[row][i]:
            return False

    # Check upper diagonal on left side
    if board[max(row - 1, 0)][max(col - 1, 0)]:
        return False

    # Check lower diagonal on left side
    if board[min(row + 1, GRID_SIZE - 1)][max(col - 1, 0)] == 1:
        return False

    return True


def solve_NQ_until(board, col):
    if col >= GRID_SIZE:
        return True

    # Consider this column and try placing
    # this queen in all rows one by one
    for i in range(GRID_SIZE):

        if is_safe(board, i, col):
            # Place this queen in board[i][col]
            board[i][col] = 1

            # recur to place rest of the queens
            if solve_NQ_until(board, col + 1):
                return True

            # If placing queen in board[i][col]
            # doesn't lead to a solution, then
            # queen from board[i][col]
            board[i][col] = 0

    # if the queen can not be placed in any row in
    # this column col  then return false
    return False


def random_solve_NQ_until(board, col):
    if col >= GRID_SIZE:
        return board

    valid_boards = []
    for i in range(GRID_SIZE):
        if is_safe(board, i, col):
            board_copy = copy_board(board)
            board_copy[i][col] = 1

            # if a feasible solution exists...
            if solve_NQ_until(copy_board(board_copy), col + 1):
                valid_boards.append(board_copy)
                continue

    if not valid_boards:
        return None
    else:
        # choose a random board
        random_board = random.choice(valid_boards)

        # solve rest of puzzle (randomly)
        random_solved_board = random_solve_NQ_until(random_board, col + 1)
        return random_solved_board


def generate_random_board_posns():
    board = None
    while not board:
        # keep trying to generate board until it works
        empty_board = [[0 for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]
        board = random_solve_NQ_until(empty_board, 0)

    # sanity check
    for i in range(len(board)):
        for j in range(len(board[i])):
            if not board[i][j]:
                continue

            board[i][j] = 0
            assert is_safe(board, i, j)
            board[i][j] = 1

    posns = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j]:
                posns.append((i, j))

    return posns
