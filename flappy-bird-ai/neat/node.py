from __future__ import annotations
from typing import List, TYPE_CHECKING
import math

if TYPE_CHECKING:
    from .connection import ConnectionGene

class Node():
    """A node in the network."""
    def __init__(self, num) -> None:
        self.num = num
        self.input_sum = 0
        self.output = 0
        self.out_connections : List[ConnectionGene] = []
        self.layer = 0
    
    def forward(self) -> None:
        def sigmoid(x):
            return 1. / (1 + math.exp(-x))

        if self.layer != 0:
            self.output = sigmoid(self.input_sum)
        
        for conn in self.out_connections:
            if conn.enabled:
                conn.to_node.input_sum += conn.weight * self.output
    
    def is_connected(self, n : Node) -> bool:
        if self.layer == n.layer:
            return False

        if self.layer < n.layer:
            for conn in self.out_connections:
                if conn.to_node == n:
                    return True
        else:
            for conn in self.out_connections:
                if conn.to_node == self:
                    return True

        return False

    def clone(self) -> Node:
        clone = Node(self.num)
        clone.layer = self.layer
        return clone