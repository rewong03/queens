import pygame
import pygame.freetype

class Button:
    def __init__(self, text_str, button_size, font):
        self.text_str = text_str
        self.font = font
        self.text_rect = font.get_rect(text_str)

        self.button_rect = pygame.Rect((0, 0), button_size)
        self.text_rect.center = self.button_rect.center

    def set_position(self, posn):
        self.button_rect.center = posn
        self.text_rect.center = self.button_rect.center

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), self.button_rect, 0, 3)
        self.font.render_to(screen, self.text_rect.topleft, self.text_str, (0, 0, 0))

    def is_in_bounds(self, posn):
        i, j = posn

        return (i >= self.button_rect.x and i <= (self.button_rect.x + self.button_rect.width) and
            j >= self.button_rect.y and j <= (self.button_rect.y + self.button_rect.height))
