import pygame
import numpy as np
import math
from constants.screen import WIDTH, HEIGHT
from constants.game import APPEAR_TIME, MAX_RADIUS, CIRCLE_NUM, RISING_SPEED
from constants.utils import RED, WHITE

class Target:
    def __init__(self, window):
        self.window = window
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
                pygame.draw.circle(self.window, current_color, self.center, current_radius)

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