from __future__ import annotations
from typing import List
import pygame

from neat.genome import Genome

class Player():

    pipe_pairs = None
    gravity = 3

    def __init__(self, pos=(500 / 5 * 2, 720 / 3), size=30.0, color=(250, 239, 32), pipes=None) -> None:
        self.position = pos
        self.size = size
        self.color = color
        self.velocity = 0

        self.last_pipe = 1
        self.last_input_time = None
        self.max_speed = 0.8
        
        if Player.pipe_pairs is None:
            Player.pipe_pairs = pipes

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

    def flap(self, delta_time) -> None:
        if self.last_input_time == None or delta_time - self.last_input_time >= 0.15:
            self.velocity = -self.max_speed
            self.last_input_time = delta_time

    def update(self, delta_time) -> None:
        def clamp(num, min_value, max_value):
            return max(min(num, max_value), min_value)

        self.velocity = clamp(self.velocity + Player.gravity * delta_time, -self.max_speed, self.max_speed)
        pos_y = clamp(self.position[1] + self.velocity, 0+self.size, 720-self.size)
        self.position = (self.position[0], pos_y)

        # handle collisions with ground
        if pos_y >= 720-self.size:
            self.is_alive = False

        # handle collisions with pipe
        pipe_list = []
        for pp in self.pipe_pairs:
            pipe_list += pp.get_pipes()
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

    def draw(self, surface) -> None:
        pygame.draw.circle(surface, self.color, self.position, self.size)

    # ------------------------------------------------------------------------
    # functions for NEAT

    def look(self):
        def normalize(value, old_range, new_range) -> float:
            value = (value - old_range[0]) / (old_range[0] + old_range[1])
            value = value / (new_range[0] + new_range[1]) + new_range[0]
            return value

        self.vision = [0, 0, 0, 0]
        self.vision[0] = normalize(self.velocity, (-0.75, 0.75), (-1, 1))

        closest_pipe = self.pipe_pairs[1 - self.last_pipe]

        bottom_pipe = closest_pipe.bottom_pipe
        # distance to closest pipe
        self.vision[1] = normalize(bottom_pipe.position[0] - self.position[0], (0, 720), (0, 1))
        # distance to top of bottom pipe
        self.vision[2] = normalize(bottom_pipe.position[1] - self.position[1], (0, 720), (0, 1))
        # distance to bottom of top pipe
        top_pipe = closest_pipe.top_pipe
        self.vision[3] = normalize(self.position[1] - top_pipe.position[1] + top_pipe.height, (0, 720), (0, 1))

    def think(self):
        self.decision = self.brain.feedforward(self.vision)
        if self.decision[0] > 0.6:
            self.flap()

    def calculate_fitness(self) -> None:
        self.fitness = 1 + pow(self.score, 2) + self.lifespan / 20.0

    def crossover(self, other_parent : Player) -> Player:
        child = Player()
        child.brain = self.brain.crossover(other_parent.brain)
        child.brain.generate_network()
        return child

    def clone(self) -> Player:
        """
        TODO ?
        """
        clone = Player()
        clone.brain = self.brain.clone()
        clone.fitness = self.fitness
        clone.brain.generate_network()
        clone.gen = self.gen
        clone.best_score = self.score
        return clone
