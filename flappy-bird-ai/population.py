from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from neat.connection import ConnectionHistory

from player import Player
from neat.species import Species

class Population():
    def __init__(self, pop_size : int) -> None:
        self.players : List[Player] = []
        self.best_player : Player = None
        self.best_score = 0
        self.global_best_score = 0
        self.gen = 1
        self.innovation_history : List[ConnectionHistory] = []
        self.gen_players : List[Player] = []
        self.species : List[Species] = []

        self.is_mass_extinction = False
        self.is_new_stage = False

        self.gens_since_new_world = 0

        for _ in range(pop_size):
            self.players.append(Player())
            self.players[-1].brain.mutate(self.innovation_history)
            self.players[-1].brain.generate_network()

    def get_current_best(self) -> Player:
        for p in self.players:
            if p.is_alive:
                return p
        return self.players[0]

    def update_alive(self, surface, delta_time) -> None:
        for p in self.players:
            if p.is_alive:
                # TODO: might add multiple steps in one update
                p.look()
                p.think()
                p.update(delta_time)

            # TODO: add selective draw to show only some of the players
            p.draw(surface)

            if p.score > self.global_best_score:
                self.global_best_score = p.score

    def done(self) -> bool:
        """
        Returns if players are all dead
        """
        for p in self.players:
            if p.is_alive:
                return False
        return True

    def select_best_player(self) -> None:
        temp_best = self.species[0].players[0]
        temp_best.gen = self.gen

        if temp_best.score > self.best_score:
            self.gen_players.append(temp_best.clone())
            print(f'Old best: {self.best_score}\tNew best: {temp_best.score}')
            self.best_score = temp_best.score
            self.best_player = temp_best.clone()

    def natural_selection(self) -> None:
        """
        Make new generation when all players are dead
        """
        prev_best = self.players[0]
        
        self.speciate()
        self.calculate_fitness()
        self.sort_species()
        if self.is_mass_extinction:
            self.mass_extinction()
            self.is_mass_extinction = False

        self.cull_species()
        self.select_best_player()
        self.kill_species()

        avg_sum = self.get_avg_fitness_sum()
        children : List[Player] = []
        for s in self.species:
            children.append(s.champ.clone())

            num_children = s.avg_fitness // avg_sum * len(self.players)

            for _ in range(num_children - 1):
                children.append(s.make_child(self.innovation_history))

        # if not enough, then get clones from best player and best species
        if len(children) < len(self.players):
            children.append(prev_best.clone())

        while len(children) < len(self.players):
            children.append(self.species[0].make_child(self.innovation_history))

        self.players = children.copy()
        self.gen += 1
        for p in self.players:
            p.brain.generate_network()

    def speciate(self) -> None:
        for s in self.species:
            s.players = []

        for p in self.players:
            species_found = False

            # look for similar species and add to it
            for s in self.species:
                if s.is_same_species(p.brain):
                    s.add_to_species(p)
                    species_found = True
                    break
            
            # if no similar species found, then make new one
            if not species_found:
                self.species.append(Species(p))

    def calculate_fitness(self):
        for p in self.players:
            p.calculate_fitness()

    def sort_species(self) -> None:
        for s in self.species:
            s.sort_species()

        temp = []

        while len(self.species) > 0:
            max_val = 0
            max_idx = 0
            
            for i, s2 in enumerate(self.species):
                if s2.best_fitness > max_val:
                    max_val = s2.best_fitness
                    max_idx = i
            
            temp.append(self.species[max_idx])
            del self.species[max_idx]

        self.species = temp.copy()

    def kill_species(self) -> None:
        """
        Kills species that are stale (haven't improved in 15 generations) or bad (won't give a child)
        """
        i = 0
        avg_sum = self.get_avg_fitness_sum()
        while i < len(self.species):
            if (self.species[i].staleness >= 15) or (self.species[i].avg_fitness / avg_sum * len(self.players) < 1):
                del self.species[i]
            else:
                i += 1

    def cull_species(self) -> None:
        """
        Kill bottom half of each species
        """
        for s in self.species:
            s.cull()
            s.fitness_sharing()
            s.set_avg_fitness()

    def mass_extinction(self) -> None:
        """
        Keep only top 5 species
        """
        self.species = self.species[:5]

    def get_avg_fitness_sum(self):
            avg_sum = 0
            for s in self.species:
                avg_sum += s.avg_fitness
            return avg_sum
