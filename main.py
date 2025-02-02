import pygame
import numpy as np
import math
from constants.screen import FPS, WIDTH, HEIGHT
from constants.utils import FONT_NAME, RED, WHITE, BLACK, CREAM, BACKGROUND_COLOR
from constants.game import APPEAR_TIME, MAX_RADIUS, CIRCLE_NUM, RISING_SPEED
from constants.state import State
from characters.target import Target
from characters.menu import Menu
from characters.button import Button

    
class Game:
    def __init__(self, window):
        self.window = window
        self.running = False
        self.font = pygame.font.SysFont(FONT_NAME, 30, True, False)
        self.font_bigger = pygame.font.SysFont(FONT_NAME, 46, True, False)

        self.menu = Menu(window)
        self.target = Target(window)
        self.setup()

        self.return_button = Button(self.window, "X", (20, 20), (70, 70), State.MENU)

    def setup(self):
        self.winning = False
        
        self.state = State.GAME
        self.score = 0
        self.hit = 0
        self.miss = 0
        
    def run_all(self):
        while main_game.state != State.QUIT:
            state_after_menu = self.menu.run_menu()
            self.state = state_after_menu
            self.run_game()
            self.run_end_screen()
    
    def startGame(self):
        self.setup()

        self.target.reset()
        self.start_time = pygame.time.get_ticks()
        self.current_total_time = 0
        self.total_pause_time = 0
        self.pause_start_time = 0
    
    def pause(self):
        self.state = State.PAUSING
        self.pause_start_time = pygame.time.get_ticks()
        self.current_total_time = pygame.time.get_ticks() - self.start_time - self.total_pause_time

    def unpause(self):
        self.state = State.GAME
        pause_interval = pygame.time.get_ticks() - self.pause_start_time
        self.total_pause_time += pause_interval
        self.target.updatePauseTime(pause_interval)

    def blit_center(self, text, position, color = BLACK, bigger = False):
        if bigger:
            text_render = self.font_bigger.render(text, 1, color)
        else:
            text_render = self.font.render(text, 1, color)

        text_rect = text_render.get_rect()
        center_x = position[0] - text_rect.width // 2
        self.window.blit(text_render, (center_x, position[1]))

    def drawScoreboard(self):
        score = np.zeros(6)
        if len(self.target.raw_hit_time) != 0:
            result = round(np.nanmean(self.target.raw_hit_time[:5])/1000, 3)
            score[0] = 0 if np.isnan(result) else result
            result = round(np.nanmean(self.target.raw_hit_time[5:10])/1000, 3)
            score[1] = 0 if np.isnan(result) else result
            for i in range(2, 6):
                result = round(np.nanmean(self.target.raw_hit_time[(i - 1)*10:i*10])/1000, 3)
                score[i] = 0 if np.isnan(result) else result

        # draw border
        vertical_length = 400
        horizontal_length = 500
        row_diff = vertical_length/8 # We have 8 row to print
        col_center_diff = horizontal_length/4 + 10
        # vertical line
        pygame.draw.line(self.window, BLACK, (WIDTH/2, HEIGHT/2 - vertical_length/2), (WIDTH/2, HEIGHT/2 + vertical_length/2), 5)
        # horizontal line
        pygame.draw.line(self.window, BLACK, (WIDTH/2 - horizontal_length/2, HEIGHT/2 - 2.5*row_diff), (WIDTH/2 + horizontal_length/2, HEIGHT/2 - 2.5*row_diff), 5)
        self.blit_center("Score", (WIDTH/2 - col_center_diff, HEIGHT/2 - vertical_length/2), bigger=True)
        self.blit_center("Time", (WIDTH/2 + col_center_diff, HEIGHT/2 - vertical_length/2), bigger=True)
        # print score
        colors = [(58, 65, 98), (51, 110, 131), (255, 245, 208), (247, 206, 114), (247, 114, 105), (208, 79, 69)]
        for i in range(6):
            self.blit_center(str(score[i]), (WIDTH/2 + col_center_diff, HEIGHT/2 - 2*row_diff + i*row_diff), colors[i])
        self.blit_center("0-5", (WIDTH/2 - col_center_diff, HEIGHT/2 - 2*row_diff), colors[0])
        self.blit_center("5-10", (WIDTH/2 - col_center_diff, HEIGHT/2 - 1*row_diff), colors[1])
        for i in range(2, 6):
            self.blit_center(f"{(i - 1)*10}-{i*10}", (WIDTH/2 - col_center_diff, HEIGHT/2 - 2*row_diff + i*row_diff), colors[i])

    def drawHUD(self):
        # score
        score_text = self.font.render("Score: " + str(self.score), 1, CREAM)
        self.window.blit(score_text, (20, 10))
        # hit rate
        total_hit = self.hit + self.miss
        if total_hit == 0:
            hit_rate = 0
        else:
            hit_rate = self.hit / total_hit
        hit_rate_text = self.font.render(f"Hit rate: {str(int(hit_rate * 100))}%", 1, CREAM)
        self.window.blit(hit_rate_text, (20, 50))

    def drawPausing(self):
        # draw pause text and scoreboard
        self.window.fill(BACKGROUND_COLOR)
        self.target.draw()
        total_time_text = self.font.render(f"Time: {str(round(self.current_total_time/1000, 1))}s", 1, CREAM)
        self.window.blit(total_time_text, (20, HEIGHT - 50))
        pause_text = self.font_bigger.render("Pausing", 1, BLACK)
        self.window.blit(pause_text, pause_text.get_rect(center=(WIDTH/2, HEIGHT/2)))
        self.drawScoreboard()
        self.drawHUD()
        pygame.display.update()

    def drawGame(self):
        self.window.fill(BACKGROUND_COLOR)
        self.drawHUD()
        self.target.draw()         
        pygame.display.update()

    def drawEndScreen(self):
        self.window.fill(BACKGROUND_COLOR)
        self.drawScoreboard()
        self.blit_center("Press ESC to return", (WIDTH/2, HEIGHT - 80))
        self.return_button.draw()
        pygame.display.update()

    def drawCountdownToStartGame(self):
        elapsed_time = 0
        start_time = pygame.time.get_ticks()/1000
        while elapsed_time <= 3:
            elapsed_time = pygame.time.get_ticks()/1000 - start_time
            if (0 <= elapsed_time <= 1):
                countdown_text = self.font_bigger.render("3", 1, CREAM)
            elif (1 < elapsed_time < 2):
                countdown_text = self.font_bigger.render("2", 1, CREAM)
            else:
                countdown_text = self.font_bigger.render("1", 1, CREAM)

            self.window.fill(BACKGROUND_COLOR)
            self.drawHUD()
            self.window.blit(countdown_text, countdown_text.get_rect(center=(WIDTH/2, HEIGHT/2)))
            # check quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            pygame.display.update()

    def checkClick(self, click_pos):
        if self.state == State.GAME:
            result = self.target.checkClick(click_pos)
            if result == 1:
                self.score += 1
                self.hit += 1
            else:
                self.miss += 1
        if self.state == State.END_SCREEN:
            result = self.return_button.checkClick(click_pos)
            if result == State.MENU:
                self.state = State.MENU

    def updateGame(self):
        global APPEAR_TIME
        global MAX_RADIUS
        # rules
        if self.score == 5:
            APPEAR_TIME = 1
        if self.score == 10:
            APPEAR_TIME = 0.75
        if self.score == 20:
            MAX_RADIUS = 67.5
        if self.score == 30:
            MAX_RADIUS = 60
        if self.score == 40:
            MAX_RADIUS = 52.5
        if self.score == 50:
            self.winning = True
            self.state = State.END_SCREEN
        self.target.update()
        self.drawGame()

    def updateAll(self):
        if self.state == State.GAME:
            self.updateGame()
        elif self.state == State.PAUSING:
            self.drawPausing()
        elif self.state == State.END_SCREEN:
            self.drawEndScreen()

    def run_end_screen(self):
        while self.state == State.END_SCREEN:
            self.drawEndScreen()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = State.QUIT
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = State.MENU
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click_pos = pygame.mouse.get_pos()
                        self.checkClick(click_pos)

    def run_game(self):
        self.setup()
        self.drawCountdownToStartGame()
        self.startGame()
        while self.state == State.GAME or self.state == State.PAUSING:
            clock.tick(FPS)
        
            self.updateAll()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = State.QUIT
                    pygame.quit()
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        click_pos = pygame.mouse.get_pos()
                        self.checkClick(click_pos)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        if self.state == State.GAME:
                            self.pause()
                        else:
                            self.unpause()
                    # add hidden key
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                        self.running = False
                        self.state = State.END_SCREEN
        
pygame.init()
pygame.display.set_caption("Clicker Game")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# init main_game
main_game = Game(screen)
main_game.run_all()

pygame.quit()