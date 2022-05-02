import pygame
from enum import Enum

class Status(Enum):
    ALIVE = 1
    DEAD = 2

class Player():
    def __init__(self, pos, size, color):
        self.position = pos
        self.size = size
        self.color = color
        self.velocity = 0

        self.last_pipe = 1
        self.last_input_time = None

        self.score = 0
        self.status = Status.ALIVE

    def handle_input(self, delta_time):
        if self.last_input_time == None or delta_time - self.last_input_time >= 0.15:
            self.velocity = -0.7
            self.last_input_time = delta_time

    def update(self, gravity, delta_time, pipe_list):
        def clamp(num, min_value, max_value):
            return max(min(num, max_value), min_value)

        self.velocity += gravity * delta_time
        pos_y = clamp(self.position[1] + self.velocity, 0+self.size, 720-self.size)
        self.position = (self.position[0], pos_y)

        # handle collisions with pipe
        for i, pipe in enumerate(pipe_list):
            collide_x = self.position[0] + self.size > pipe.position[0] and self.position[0] - self.size < pipe.position[0] + pipe.width
            collide_y = self.position[1] + self.size > pipe.position[1] and self.position[1] - self.size < pipe.position[1] + pipe.height

            if collide_x and collide_y:
                self.status = Status.DEAD

            # check if past pipe and increment score
            dist_past = (self.position[0] - self.size) - (pipe.position[0] + pipe.width)
            if dist_past > 0 and i // 2 != self.last_pipe:
                self.score += 1
                self.last_pipe = i // 2
                print(f'Score: {self.score}')

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.size)
