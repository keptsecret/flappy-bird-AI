from __future__ import annotations
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from .node import Node
    from .genome import Genome

class ConnectionGene():
    """A connection between two nodes."""

    def __init__(self, from_n : Node, to_n : Node, w : float, inno : int):
        self.from_node = from_n
        self.to_node = to_n
        self.weight = w
        self.enabled = True
        self.innovation_num = inno

    def mutate_weight(self):
        def clamp(num, min_value, max_value):
            return max(min(num, max_value), min_value)

        p = random.random()
        if (p < 0.1):
            self.weight += random.uniform(-1, 1)
        else:
            self.weight += clamp(random.gauss(0, 1) / 50, -1, 1)

    def clone(self, from_n : Node, to_n : Node):
        clone = ConnectionGene(from_n, to_n, self.weight, self.innovation_num)
        clone.enabled = self.enabled
        return clone

class ConnectionHistory():
    def __init__(self, from_n : Node, to_n : Node, inno : int, innos : list[int]):
        self.from_node = from_n
        self.to_node = to_n
        self.innovation_num = inno
        self.innovation_nums = innos.copy()

    def matches(self, genome : Genome, from_n : Node, to_n : Node):
        """Returns whether param genome matches this genome, including all connections"""
        
        if len(genome.genes) == len(self.innovation_nums):
            if from_n.num == self.from_node and to_n.num == self.to_node:
                for conn in genome.genes:
                    if conn.innovation_num not in self.innovation_nums:
                        return False

            return True
        return False