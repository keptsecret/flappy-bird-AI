from __future__ import annotations
import pygame

from neat.genome import Genome

class Player():
    def __init__(self, pos, size, color) -> None:
        self.position = pos
        self.size = size
        self.color = color
        self.velocity = 0

        self.last_pipe = 1
        self.last_input_time = None

        # NEAT stuff
        self.fitness = 0
        self.vision = []        # input for NN
        self.decision = []      # output of NN
        self.unadjusted_fitness = None
        self.lifespan = 0
        self.best_score = 0     # might not be needed
        self.score = 0
        self.is_alive = True
        self.gen = 0

        self.genome_inputs = 4
        self.genome_outputs = 1
        self.brain = Genome(self.genome_inputs, self.genome_outputs)

    def handle_input(self, delta_time) -> None:
        if self.last_input_time == None or delta_time - self.last_input_time >= 0.15:
            self.velocity = -0.7
            self.last_input_time = delta_time

    def update(self, gravity, delta_time, pipe_list) -> None:
        def clamp(num, min_value, max_value):
            return max(min(num, max_value), min_value)

        self.velocity += gravity * delta_time
        pos_y = clamp(self.position[1] + self.velocity, 0+self.size, 720-self.size)
        self.position = (self.position[0], pos_y)

        # handle collisions with ground
        if pos_y >= 720-self.size:
            self.is_alive = False

        # handle collisions with pipe
        for i, pipe in enumerate(pipe_list):
            collide_x = self.position[0] + self.size > pipe.position[0] and self.position[0] - self.size < pipe.position[0] + pipe.width
            collide_y = self.position[1] + self.size > pipe.position[1] and self.position[1] - self.size < pipe.position[1] + pipe.height

            if collide_x and collide_y:
                self.is_alive = False

            # check if past pipe and increment score
            dist_past = (self.position[0] - self.size) - (pipe.position[0] + pipe.width)
            if dist_past > 0 and i // 2 != self.last_pipe:
                self.score += 1
                self.last_pipe = i // 2
                print(f'Score: {self.score}')

    def draw(self, surface) -> None:
        pygame.draw.circle(surface, self.color, self.position, self.size)

    def crossover(self, other_parent : Player) -> Player:
        pass

    def clone(self) -> Player:
        """
        TODO ?
        """
        pass
