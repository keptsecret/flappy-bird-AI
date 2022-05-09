from __future__ import annotations
from typing import List, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from ..player import Player
    from .genome import Genome
    from .connection import ConnectionHistory

class Species():
    def __init__(self, player : Player) -> None:
        self.players : List[Player] = []
        self.best_fitness = 0
        self.champ = None
        self.avg_fitness = 0
        self.staleness = 0
        self.rep = None

        self.excess_cof = 1
        self.weight_diff_cof = 0.5
        self.compat_thresh = 3

        if player != None:
            self.players.append(player)
            self.best_fitness = player.fitness
            self.rep = player.brain.clone()
            self.champ = player.clone()         # might not use, if not implement replay

    def is_same_species(self, g : Genome) -> bool:
        """
        Returns whether this and param genome is in same species i.e., similar genes
        """
        excess_and_disjoint = self.get_excess_disjoint(g, self.rep)
        avg_weight_diff = self.avg_weight_diff(g, self.rep)

        normalizer = max(len(g.genes), 1)
        compat = (self.excess_cof * excess_and_disjoint / normalizer) + (self.weight_diff_cof * avg_weight_diff)    # compatibility formula
        return compat < self.compat_thresh

    def get_excess_disjoint(self, brain1 : Genome, brain2 : Genome) -> float:
        """
        Returns number of excess and disjoint genes (those that don't match)
        """
        matching = 0.0
        for conn1 in brain1.genes:
            for conn2 in brain2.genes:
                if conn1.innovation_num == conn2.innovation_num:
                    matching += 1
                    break
        
        return len(brain1.genes) + len(brain2.genes) - 2 * matching

    def avg_weight_diff(self, brain1 : Genome, brain2 : Genome) -> float:
        """
        Returns average weight difference between matching genes in genomes
        """
        if len(brain1.genes) == 0 or len(brain2.genes) == 0:
            return 0

        matching = 0.0
        total_diff = 0.0
        for conn1 in brain1.genes:
            for conn2 in brain2.genes:
                if conn1.innovation_num == conn2.innovation_num:
                    matching += 1
                    total_diff += abs(conn1.weight - conn2.weight)
                    break

        if matching == 0:
            return 100

        return total_diff / matching

    def add_to_species(self, player : Player) -> None:
        self.players.append(player)

    def sort_species(self) -> None:
        """
        Sorts players by fitness, in decreasing order
        """
        temp = []

        while len(self.players) > 0:
            max_val = 0
            max_idx = 0
            
            for i, p2 in enumerate(self.players):
                if p2.fitness > max_val:
                    max_val = p2.fitness
                    max_idx = i
            
            temp.append(self.players[max_idx])
            del self.players[max_idx]

        self.players = temp.copy()
        if len(self.players) == 0:
            self.staleness = 200
            return
        
        if self.players[0].fitness > self.best_fitness:
            self.staleness = 0
            self.best_fitness = self.players[0].fitness
            self.rep = self.players[0].brain.clone()
            self.champ = self.players[0].clone()
        else:
            self.staleness += 1

    def set_avg_fitness(self) -> None:
        total = 0
        for p in self.players:
            total += p.fitness
        
        self.avg_fitness = total / len(self.players)

    def make_child(self, innovation_hist : List[ConnectionHistory]) -> Player:
        """
        Makes a child from all players in this species
        """

        if (random.random() < 0.25):
            baby = self.select_player().clone()
        else:
            p1 = self.select_player()
            p2 = self.select_player()

            if p1.fitness < p2.fitness:
                baby = p2.crossover(p1)
            else:
                baby = p1.crossover(p2)
        
        baby.brain.mutate(innovation_hist)
        return baby

    def select_player(self) -> Player:
        """
        Returns a player based on fitness semi-randomly
        """
        fitness_sum = 0
        for p in self.players:
            fitness_sum += p.fitness
        
        rand = random.random() * fitness_sum
        running = 0
        for p in self.players:
            running += p.fitness
            if running > rand:
                return p
        
        return self.players[0]

    def cull(self) -> None:
        """
        Removes bottom half of players
        """
        p_len = len(self.players)
        if p_len > 2:
            self.players = self.players[:p_len // 2]

    def fitness_sharing(self) -> None:
        """
        Protect unique players by scaling down players' fitnesses with number of players in its species
        """
        for p in self.players:
            p.fitness /= len(self.players)
