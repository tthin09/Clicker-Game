import pygame
import sys
sys.path.append("..")
from constants.state import State
from characters.button import Button
from constants.screen import WIDTH, HEIGHT
from constants.utils import FONT_NAME, RED, WHITE, CREAM, BACKGROUND_COLOR
from constants.game import CIRCLE_NUM

class Menu:
    def __init__(self, window):
        self.window = window
        self.font = pygame.font.SysFont(FONT_NAME, 30, True, False)
        self.font_bigger = pygame.font.SysFont(FONT_NAME, 46, True, False)
        self.state = State.MENU
        self.running = False

        self.menu_buttons = []
        self.rules_buttons = []
        self.createButtons()

    def run_menu(self):
        self.state = State.MENU
        while self.state == State.MENU or self.state == State.RULES:
            self.drawAll()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = State.QUIT
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click_pos = pygame.mouse.get_pos()
                        self.checkClick(click_pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = State.QUIT
                        pygame.quit()
        return self.state
      
    def createButtons(self):
        width = 200
        height = 100
        self.menu_buttons.append(Button(self.window, "Play", (WIDTH/2 - width/2, HEIGHT/2 - 50 - height), (width, height), State.GAME))
        self.menu_buttons.append(Button(self.window, "Rules", (WIDTH/2 - width/2, HEIGHT/2 + 50), (width, height), State.RULES))

        self.rules_buttons.append(Button(self.window, "X", (20, 20), (70, 70), State.MENU))

    def drawAll(self):
        self.window.fill(BACKGROUND_COLOR)
        if self.state == State.MENU:
            for button in self.menu_buttons:
                button.draw()
        elif self.state == State.RULES:
            self.rules_buttons[0].draw()
            self.drawRules()
        pygame.display.update()

    def drawLongText(self, paragraph, corner, width):
        collection = [line.split(' ') for line in paragraph.splitlines()]
        space = self.font.size(" ")[0]
        x, y = corner
        for line in collection:
            for word in line:
                word_draw = self.font.render(word, True, CREAM)
                word_width, word_height = word_draw.get_size()
                if (x + word_width) >= (corner[0] + width):
                    x = corner[0]
                    y += word_height
                self.window.blit(word_draw, (x, y))
                x += word_width + space
            x = corner[0]
            y += word_height

    def drawRules(self):
        # draw rules
        rules = "Try to click the circle as fast as possible! \nAt 5/10 points, your circle will disappear faster. \nFor 20/30/40 circles, your circle will be smaller. \nAfter 50 circles, you win! \nYour score will be determined by your speed and accuracy."
        self.drawLongText(rules, (150, HEIGHT/2 - 150), WIDTH - 300)
        # draw example circle
        center = (WIDTH/2, HEIGHT/2 + 170)
        radius = 65
        for i in range(CIRCLE_NUM, 0, -1):
            current_radius = radius * i / CIRCLE_NUM
            current_color = RED if i % 2 == 1 else WHITE
            pygame.draw.circle(self.window, current_color, center, current_radius)

    def checkClick(self, click_pos):
        result = None
        if self.state == State.MENU:
            for button in self.menu_buttons:
                result = button.checkClick(click_pos)
                if result != None:
                    break
        elif self.state == State.RULES:
            result = self.rules_buttons[0].checkClick(click_pos)

        if result != None:
            self.state = result