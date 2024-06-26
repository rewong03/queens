from constants import *
from board import Board
from utils import grid_to_screen, screen_to_grid
from colors import COLOR_TO_TUPLE
from tile import TileState
from button import Button
import argparse
import os
import json
from multiprocessing import Queue, Process

import pygame
import pygame.freetype
import time


def draw_board_background(screen):
    # Fill the background with white
    screen.fill((255, 255, 255))

    # draw vertical lines
    pygame.draw.rect(
        screen, (0, 0, 0), pygame.Rect(0, 0, LINE_THICKNESS // 2, GRID_PIXEL_HEIGHT)
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            GRID_PIXEL_WIDTH - (LINE_THICKNESS // 2),
            0,
            LINE_THICKNESS,
            GRID_PIXEL_HEIGHT,
        ),
    )
    for x in range(
        (GRID_PIXEL_WIDTH // 8) - (LINE_THICKNESS // 2),
        GRID_PIXEL_WIDTH,
        GRID_PIXEL_WIDTH // 8,
    ):
        # print(x)
        pygame.draw.rect(
            screen, (0, 0, 0), pygame.Rect(x, 0, LINE_THICKNESS, GRID_PIXEL_HEIGHT)
        )

    # draw horizontal lines
    pygame.draw.rect(
        screen, (0, 0, 0), pygame.Rect(0, 0, GRID_PIXEL_WIDTH, LINE_THICKNESS // 2)
    )
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        pygame.Rect(
            0,
            GRID_PIXEL_WIDTH - (LINE_THICKNESS // 2),
            GRID_PIXEL_WIDTH,
            LINE_THICKNESS,
        ),
    )
    for y in range(
        (GRID_PIXEL_HEIGHT // 8) - (LINE_THICKNESS // 2),
        GRID_PIXEL_HEIGHT,
        GRID_PIXEL_HEIGHT // 8,
    ):
        pygame.draw.rect(
            screen, (0, 0, 0), pygame.Rect(0, y, GRID_PIXEL_WIDTH, LINE_THICKNESS)
        )


def draw_board(screen, font, board, check_mode=False):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            tile = board.get_tile((i, j))
            tile_center = grid_to_screen((i, j))

            # add colors
            color = tile.color
            r = pygame.Rect(
                (0, 0),
                (
                    GRID_PIXEL_WIDTH // 8 - LINE_THICKNESS,
                    GRID_PIXEL_HEIGHT // 8 - LINE_THICKNESS,
                ),
            )
            r.center = tile_center
            pygame.draw.rect(screen, COLOR_TO_TUPLE[color], r)

            mark_color = (0, 0, 0)
            if check_mode:
                # green mark if correct, red otherwise
                if tile.state == TileState.MARKED and tile.is_queen:
                    mark_color = (255, 0, 0)
                else:
                    mark_color = (0, 255, 0)

            queen_color = None
            if check_mode:
                # green queen if correct, red otherwise
                if tile.state == TileState.QUEEN and not tile.is_queen:
                    queen_color = (255, 0, 0)
                else:
                    queen_color = (0, 255, 0)

            # draw state sprites
            if tile.state == TileState.MARKED:
                text_str = "x"
                text_rect = font.get_rect(text_str)
                text_rect.center = tile_center
                font.render_to(screen, text_rect.topleft, text_str, mark_color)
            elif tile.state == TileState.QUESTION:
                text_str = "?"
                text_rect = font.get_rect(text_str)
                text_rect.center = tile_center
                font.render_to(screen, text_rect.topleft, text_str, (0, 0, 0))
            elif tile.state == TileState.QUEEN:
                scale_factor = 1
                if board.is_solved():
                    scale_factor = tile.get_next_scale_factor()

                img = pygame.image.load("assets/my_queen.png").convert_alpha()

                if queen_color:
                    img.fill(queen_color, special_flags=pygame.BLEND_ADD)

                img = pygame.transform.scale_by(img, 0.10 * scale_factor)
                img_rect = img.get_rect()
                img_rect.center = tile_center
                screen.blit(img, img_rect.topleft)
                # r = pygame.Rect((0, 0), (30 * scale_factor, 30 * scale_factor))
                # r.center = tile_center
                # pygame.draw.rect(screen, queen_color, r)


def draw_time(screen, font, elapsed_time):
    elapsed_minutes = elapsed_time // 60
    elapsed_seconds = elapsed_time % 60

    if elapsed_minutes < 10:
        elapsed_minutes = f"0{elapsed_minutes}"
    else:
        elapsed_minutes = str(elapsed_minutes)

    if elapsed_seconds < 10:
        elapsed_seconds = f"0{elapsed_seconds}"
    else:
        elapsed_seconds = str(elapsed_seconds)

    text_str = f"{elapsed_minutes}:{elapsed_seconds}"
    text_rect = font.get_rect(text_str)
    text_rect.center = (GRID_PIXEL_WIDTH + (SIDE_PANEL_WIDTH // 2), text_rect.height)
    font.render_to(screen, text_rect.topleft, text_str, (0, 0, 0))


def handle_grid_mouse_click(board, screen_posn, button):
    if board.is_solved():
        return

    i, j = screen_posn

    if i >= 0 and i < GRID_PIXEL_WIDTH and j >= 0 and j < GRID_PIXEL_HEIGHT:
        tile_i, tile_j = screen_to_grid(screen_posn)
        tile = board.get_tile((tile_i, tile_j))

        if button == 1:
            if tile.state != TileState.QUESTION:
                next_state = TileState((tile.state.value + 1) % (len(TileState) - 1))

                other_queens = any(
                    other_tile.state == TileState.QUEEN
                    for other_tile in board.color_groups[tile.color]
                )
                if next_state == TileState.QUEEN:
                    if Board._is_valid_queen_posn(board, (tile_i, tile_j)):
                        tile.state = next_state
                    else:
                        tile.state = TileState.EMPTY
                else:
                    tile.state = next_state
        elif button == 3:
            if tile.state == TileState.EMPTY:
                tile.state = TileState.QUESTION
            elif tile.state == TileState.QUESTION:
                tile.state = TileState.EMPTY


def _generate_boards_in_background(board_q, kill_q):
    while True:
        # check if we have been killed :(
        try:
            kill_q.get_nowait()
            print("Dying!")
            return
        except:
            pass

        print("Generating board!")
        board = Board.generate_random_board()
        print("Done generating!")

        while True:
            try:
                kill_q.get(False)
                print("Dying!")
                return
            except:
                pass

            try:
                board_q.put_nowait(board)
                print("Generated board!")
                break
            except:
                time.sleep(1)


if __name__ == "__main__":
    """
    TODO:
    - let users choose between a board size of 8, 9, 10 tiles
    - let choosers choose a higher difficulty
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # setup a directory for state
    if not os.path.exists(".queens"):
        os.mkdir(".queens")

    # grabbed cached boards
    cached_boards = []
    if os.path.exists(".queens/cache.json"):
        with open(".queens/cache.json") as f:
            cached_boards = json.load(f)

    print(f"Read {len(cached_boards)}")

    board_queue = Queue(5)
    for board in cached_boards[:5]:
        board_queue.put(Board.from_dict(board))

    # spawn a worker process to get boards in the background
    kill_q = Queue()
    board_generator = Process(
        target=_generate_boards_in_background, args=(board_queue, kill_q), daemon=True
    )
    board_generator.start()

    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()

    # Set up the drawing window
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    board = board_queue.get()
    board.set_up_win_animation()
    print("Got board!")

    large_font = pygame.freetype.SysFont("Comic Sans MS", 60)
    small_font = pygame.freetype.SysFont("Comic Sans MS", 20)

    # initialize buttons
    new_game_button = Button("New Game", (200, 50), small_font)
    new_game_button.set_position((GRID_PIXEL_WIDTH + (SIDE_PANEL_WIDTH // 2), 150))

    check_board_button = Button("Check Board", (200, 50), small_font)
    check_board_button.set_position((GRID_PIXEL_WIDTH + (SIDE_PANEL_WIDTH // 2), 250))

    give_up_button = Button("Give Up :(", (200, 50), small_font)
    give_up_button.set_position((GRID_PIXEL_WIDTH + (SIDE_PANEL_WIDTH // 2), 350))

    debug_button = Button("Debug", (200, 50), small_font)
    debug_button.set_position((GRID_PIXEL_WIDTH + (SIDE_PANEL_WIDTH // 2), 450))

    # state for button logic
    check_until = 0  # time at which to stop showing "check" hints

    start_time = time.time()
    elapsed_time = int(time.time() - start_time)

    # Run until the user asks to quit
    running = True
    while running:
        if not board.is_solved():
            elapsed_time = int(time.time() - start_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONUP:
                handle_grid_mouse_click(board, pygame.mouse.get_pos(), event.button)

                # handle pressing screen buttons
                if (
                    new_game_button.is_in_bounds(pygame.mouse.get_pos())
                    and event.button == 1
                ):
                    new_game_button.text_str = "Loading..."
                    new_game_button.draw(screen)
                    pygame.display.flip()

                    while True:
                        try:
                            board = board_queue.get_nowait()
                            board.set_up_win_animation()
                            break
                        except:
                            pass

                        for event_2 in pygame.event.get():
                            if event_2.type == pygame.QUIT:
                                running = False
                                break

                        if not running:
                            break

                    new_game_button.text_str = "New Game"
                    new_game_button.draw(screen)
                    pygame.display.flip()

                    start_time = time.time()

                if (
                    check_board_button.is_in_bounds(pygame.mouse.get_pos())
                    and event.button == 1
                ):
                    check_until = time.time() + 1

                if (
                    give_up_button.is_in_bounds(pygame.mouse.get_pos())
                    and event.button == 1
                ):
                    for i in range(GRID_SIZE):
                        for j in range(GRID_SIZE):
                            if (i, j) in board.queen_posns:
                                board.get_tile((i, j)).state = TileState.QUEEN
                            else:
                                board.get_tile((i, j)).state = TileState.EMPTY

                if (
                    debug_button.is_in_bounds(pygame.mouse.get_pos())
                    and event.button == 1
                    and args.debug
                ):
                    print(board)

        # draw everything
        draw_board_background(screen)
        draw_board(screen, small_font, board, check_mode=time.time() < check_until)
        draw_time(screen, large_font, elapsed_time)

        new_game_button.draw(screen)
        check_board_button.draw(screen)
        give_up_button.draw(screen)

        if args.debug:
            debug_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    # stop worker process
    kill_q.put(True)
    board_generator.terminate()

    # save any remaining boards into a cache
    if os.path.exists(".queens/cache.json"):
        os.remove(".queens/cache.json")

    baords_to_cache = []
    while not board_queue.empty():
        baords_to_cache.append(board_queue.get().to_dict())

    with open(".queens/cache.json", "w") as f:
        json.dump(baords_to_cache, f)

    # Done! Time to quit.
    pygame.quit()
