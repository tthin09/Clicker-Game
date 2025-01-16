import pygame
from constants.utils import FONT_NAME, WHITE, BLACK

class Button:
    def __init__(self, window, text, corner, size, state):
        self.window = window
        self.text = text
        self.corner = corner
        self.width = size[0]
        self.height = size[1]
        self.state = state

    def draw(self):
        font = pygame.font.SysFont(FONT_NAME, 46, True, False)
        text_draw = font.render(self.text, 1, WHITE)
        # draw button
        pygame.draw.rect(self.window, WHITE, (self.corner[0], self.corner[1], self.width, self.height), width=5)
        pygame.draw.rect(self.window, BLACK, (self.corner[0] + 5, self.corner[1] + 5, self.width - 10, self.height - 10))
        # text
        text_rect = text_draw.get_rect()
        self.window.blit(text_draw, (self.corner[0] + self.width/2 - text_rect.width/2, self.corner[1] + self.height/2 - text_rect.height/2))

    def checkClick(self, click_pos):
        if (self.corner[0] <= click_pos[0] <= self.corner[0] + self.width) and (self.corner[1] <= click_pos[1] <= self.corner[1] + self.height):
            return self.state
        return None