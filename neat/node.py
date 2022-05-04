import math

from connection import ConnectionGene

class Node():
    """A node in the network."""
    def __init__(self, num):
        self.num = num
        self.input_sum = 0
        self.output = 0
        self.out_connections : list[ConnectionGene] = []
        self.layer = 0
    
    def forward(self):
        def sigmoid(x):
            return 1. / (1 + math.exp(-x))

        if self.layer != 0:
            self.output = sigmoid(self.input_sum)
        
        for conn in self.out_connections:
            if conn.enabled:
                conn.to_node.input_sum += conn.weight * self.output
    
    def is_connected(self, n):
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

    def clone(self):
        clone = Node(self.num)
        clone.layer = self.layer
        return clone