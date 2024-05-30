from constants import *


def grid_to_screen(grid_posn):
    """Take a grid position and returns the screen coordinate of
    the center of the grid position"""
    x, y = grid_posn

    tile_screen_width = GRID_PIXEL_WIDTH // GRID_SIZE
    tile_screen_height = GRID_PIXEL_HEIGHT // GRID_SIZE

    return (
        x * tile_screen_width + (tile_screen_width // 2),
        y * tile_screen_height + (tile_screen_height // 2),
    )


def screen_to_grid(screen_posn):
    """Take a screen position and returns the grid coordinate"""
    x, y = screen_posn

    tile_screen_width = GRID_PIXEL_WIDTH // GRID_SIZE
    tile_screen_height = GRID_PIXEL_HEIGHT // GRID_SIZE

    return x // (tile_screen_width), y // tile_screen_height
