import pygame
import numpy as np
import math

# screen
FPS = 60
RATIO = 16/9
WIDTH = 1200
HEIGHT = WIDTH / RATIO
FONT_NAME = "comicsans"

# color
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CREAM = (255, 245, 208)
BACKGROUND_COLOR = (32, 32, 32)

# circle (appear_time in second, 0.01 being error)
APPEAR_TIME = 1.25
MAX_RADIUS = 75
CIRCLE_NUM = 7
RISING_SPEED = MAX_RADIUS / ((APPEAR_TIME - 0.01) * 30)

class Target:
    def __init__(self):
        self.reset()

    def reset(self):
        self.radius = 0
        self.rising = True
        self.center = self.getRandomPosition()

        self.appearing = True
        self.first_appear_time = pygame.time.get_ticks()
        self.appear_time = pygame.time.get_ticks()

        self.intervals = []
        self.hit_time = []
        self.raw_hit_time = []
    
    def getRandomPosition(self):
        x = np.random.randint(MAX_RADIUS + 10, WIDTH - MAX_RADIUS - 10)
        y = np.random.randint(MAX_RADIUS + 10 + 50, HEIGHT - MAX_RADIUS - 10)
        return (x, y)
    
    def resetPosition(self):
        current_time = pygame.time.get_ticks()
        # done an interval -> reappear
        interval = current_time - self.appear_time
        if interval >= APPEAR_TIME * 1000:
            if not self.appearing:
                self.first_appear_time = pygame.time.get_ticks()
            self.appearing = True
            self.appear_time = pygame.time.get_ticks()
            self.center = self.getRandomPosition()
            self.radius = 0
            self.rising = True

            self.intervals.append(interval)
            return True
        return False

    def update(self):
        if self.radius > MAX_RADIUS:
            self.rising = False
        elif self.radius < 0:
            self.resetPosition()
        if self.appearing:
            if self.rising:
                self.radius += RISING_SPEED
            else:
                self.radius -= RISING_SPEED
    
    def draw(self):
        if self.appearing:
            for i in range(CIRCLE_NUM, 0, -1):
                current_radius = self.radius * i / CIRCLE_NUM
                current_color = RED if i % 2 == 1 else WHITE
                pygame.draw.circle(screen, current_color, self.center, current_radius)

    def checkClick(self, click_pos):
        x, y = click_pos
        distance = math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)) + 1
        if (distance <= self.radius):
            self.radius = -10
            self.rising = False
            self.appearing = False
            self.hit_time.append(pygame.time.get_ticks() - self.appear_time)
            self.raw_hit_time.append(pygame.time.get_ticks() - self.first_appear_time)
            print(f"Hit! - {self.raw_hit_time[-1]/1000:.3f}s")
            return 1
        else:
            print("Miss")
            return 0
        
    def updatePauseTime(self, pause_interval):
        self.appear_time += pause_interval
        self.first_appear_time += pause_interval

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
            pygame.draw.circle(screen, current_color, center, current_radius)

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

class State:
    MENU = "Menu"
    RULES = "Rules"
    GAME = "Game"
    PAUSING = "Pausing"
    END_SCREEN = "End screen"
    QUIT = "Quit"
    
class Game:
    def __init__(self, window):
        self.window = window
        self.running = False
        self.font = pygame.font.SysFont(FONT_NAME, 30, True, False)
        self.font_bigger = pygame.font.SysFont(FONT_NAME, 46, True, False)

        self.target = Target()
        self.setup()

        self.return_button = Button(self.window, "X", (20, 20), (70, 70), State.MENU)

    def setup(self):
        self.winning = False
        
        self.state = State.GAME
        self.score = 0
        self.hit = 0
        self.miss = 0
    
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
menu = Menu(screen)

while main_game.state != State.QUIT:
    main_game.state = menu.run_menu()
    main_game.run_game()
    main_game.run_end_screen()

pygame.quit()