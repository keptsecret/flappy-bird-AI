from __future__ import annotations
from typing import List
import pygame
import random

class Pipe():
    def __init__(self, pos_x, pos_y, width=100, height=800, color=(105, 214, 21)) -> None:
        self.init_x = pos_x
        self.init_y = pos_y
        self.position = (pos_x, pos_y)
        self.width = width
        self.height = height
        self.color = color
        self.speed = 150

    def update(self, delta_time) -> None:
        self.position = (self.position[0] - self.speed * delta_time, self.position[1])

    def draw(self, surface) -> None:
        pygame.draw.rect(surface, self.color, (self.position[0], self.position[1], self.width, self.height))

    def reset(self, pos) -> None:
        self.position = pos

class PipePair():
    def __init__(self, pos_x=510, width=100, height=800, color=(105, 214, 21)) -> None:
        bottom_pos_y = random.randint(200, 520)

        self.gap_size = 200
        self.height = height
        self.top_pipe = Pipe(pos_x, bottom_pos_y - height - self.gap_size, width, height, color)
        self.bottom_pipe = Pipe(pos_x, bottom_pos_y, width, height, color)
        self.active = False
        
    def start(self) -> None:
        self.active = True

    def update(self, delta_time) -> None:
        self.top_pipe.update(delta_time)
        self.bottom_pipe.update(delta_time)

        if self.top_pipe.position[0] + self.top_pipe.width < 0:
            bottom_pos_y = random.randint(200, 520)
            self.top_pipe.reset((self.top_pipe.init_x, bottom_pos_y - self.height - self.gap_size))
            self.bottom_pipe.reset((self.bottom_pipe.init_x, bottom_pos_y))

    def reset(self):
        bottom_pos_y = random.randint(200, 520)
        self.top_pipe.reset((self.top_pipe.init_x, bottom_pos_y - self.height - self.gap_size))
        self.bottom_pipe.reset((self.bottom_pipe.init_x, bottom_pos_y))
        self.active = False

    def draw(self, surface) -> None:
        self.top_pipe.draw(surface)
        self.bottom_pipe.draw(surface)

    def get_pipes(self) -> List[Pipe]:
        return [self.top_pipe, self.bottom_pipe]