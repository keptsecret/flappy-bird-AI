import random

from node import Node
from connection import ConnectionGene, ConnectionHistory

class Genome():
    """Contains the network representation for a specimen"""

    next_conn_num = 420

    def __init__(self, inputs, outputs, crossover=False):
        self.genes : list[ConnectionGene] = []
        self.nodes : list[Node] = []
        self.inputs = inputs
        self.outputs = outputs
        self.layers = 2
        self.next_node = 0
        self.network : list[Node] = []

        if crossover:
            return

        for i in range(self.inputs):
            self.nodes.append(Node(i))
            self.next_node += 1
            self.nodes[i].layer = 0

        for i in range(self.outputs):
            self.nodes.append(Node(i + self.inputs))
            self.next_node += 1
            self.nodes[i + self.inputs].layer = 1

        self.nodes.append(Node(self.next_node))
        self.bias_node = self.next_node
        self.next_node += 1
        self.nodes[self.bias_node].layer = 0

    def get_node(self, n_num):
        for n in self.nodes:
            if n.num == n_num:
                return n
        return None

    def fully_connect(self, innovation_hist : list[ConnectionHistory]):
        """Connects all the nodes in the network"""
        for i in range(self.inputs):
            for j in range(self.outputs):
                conn_inno_num = self.get_innovation_num(innovation_hist, self.nodes[i], self.nodes[len(self.nodes) - j - 2])
                self.genes.append(ConnectionGene(self.nodes[i], self.nodes[len(self.nodes) - j - 2], random.uniform(-1, 1), conn_inno_num))

        conn_inno_num = self.get_innovation_num(innovation_hist, self.nodes[self.bias_node], self.nodes[len(self.nodes) - 2])
        self.genes.append(ConnectionGene(self.bias_node, self.nodes[len(self.nodes) - 2], random.uniform(-1, 1), conn_inno_num))

        self.connect_nodes()

    def is_fully_connected(self):
        nodes_per_layer = []
        for l in range(self.layers):
            nodes_per_layer[l] = 0

        for n in self.nodes:
            nodes_per_layer[n.layer] += 1

        # maximum number of connections from each layer is no. of nodes in layer * no. of nodes in layers above it
        max_conns = 0
        for i in range(self.layers - 1):
            nodes_above = 0
            for j in range(i + 1, self.layers):
                nodes_above += nodes_per_layer[j]
            
            max_conns += nodes_above * nodes_per_layer[i]
        
        if max_conns <= len(self.genes):
            return True

        return False

    def connect_nodes(self):
        """Connects nodes to its targets to pass on input during feedforward"""
        for n in self.nodes:
            n.out_connections = []
        
        for conn in self.genes:
            conn.from_node.out_connections.append(conn)

    def generate_network(self):
        """Generates a list of nodes in order that they have to be run in, stored in self.network"""
        self.connect_nodes()
        self.network = []

        for l in range(self.layers):
            for n in self.nodes:
                if n.layer == l:
                    self.network.append(n)

    def feedforward(self, input_vals):
        """Sends input through network and returns the output of network"""
        for i in range(self.inputs):
            self.nodes[i].output = input_vals[i]
        self.nodes[self.bias_node].output = 1

        for n in self.network:
            n.forward()

        outputs = []
        for i in range(self.outputs):
            outputs.append(self.nodes[self.inputs + i].output)

        for n in self.network:
            n.input_sum = 0

        return outputs

    def add_node(self, innovation_hist : list[ConnectionHistory]):
        """
        Adds a random node to the network to mutate.\n
        A random connection is picked, disabled and a new node is added with 2 new connections.
        """
        if len(self.genes) == 0:
            self.add_connection(innovation_hist)
            return
        
        rand_conn = random.randint(0, len(self.genes)-1)
        while self.genes[rand_conn].from_node == self.nodes[self.bias_node] and len(self.genes) != 1:
            rand_conn = random.randint(0, len(self.genes)-1)

        self.genes[rand_conn].enabled = False

        new_node = self.next_node
        self.next_node += 1
        self.nodes.append(Node(new_node))

        # connect start of old connection to new node
        conn_inno_num = self.get_innovation_number(innovation_hist, self.genes[rand_conn].from_node, self.get_node(new_node))
        self.genes.append(ConnectionGene(self.genes[rand_conn].from_node, self.get_node(new_node), 1, conn_inno_num))

        # connect new node to end of old connection
        conn_inno_num = self.get_innovation_number(innovation_hist, self.get_node(new_node), self.genes[rand_conn].to_node)
        self.genes.append(ConnectionGene(self.get_node(new_node), self.genes[rand_conn].to_node, self.genes[rand_conn].weight, conn_inno_num))
        self.get_node(new_node).layer = self.genes[rand_conn].from_node + 1

        # connect bias to new node
        conn_inno_num = self.get_innovation_number(innovation_hist, self.nodes[self.bias_node], self.get_node(new_node))
        self.genes.append(ConnectionGene(self.nodes[self.bias_node], self.get_node(new_node), 0, conn_inno_num))

        # move nodes in layers above if needed
        if self.get_node(new_node).layer == self.genes[rand_conn].to_node.layer:
            for n in self.nodes:
                if n.layer >= self.get_node(new_node).layer:
                    n.layer += 1
        
        self.layers += 1
        self.connect_nodes()

    def add_connection(self, innovation_hist : list[ConnectionHistory]):
        """
        Picks two random nodes that aren't connected to add a connection between
        """
        if self.is_fully_connected():
            print("Connection failed: full network")
            return

        def is_invalid_connection(n1, n2):
            if self.nodes[n1].layer == self.nodes[n2].layer or self.nodes[n1].is_connected(self.nodes[n2]):
                return True
            return False
        
        # pick two nodes and check they aren't already connected and can be connected
        rand_node_1 = random.randint(0, len(self.nodes) - 1)
        rand_node_2 = random.randint(0, len(self.nodes) - 1)
        while is_invalid_connection(rand_node_1, rand_node_2):
            rand_node_1 = random.randint(0, len(self.nodes) - 1)
            rand_node_2 = random.randint(0, len(self.nodes) - 1)
        
        if self.nodes[rand_node_1].layer > self.nodes[rand_node_2].layer:
            tmp = rand_node_1
            rand_node_1 = rand_node_2
            rand_node_2 = tmp
        
        conn_inno_num = self.get_innovation_number(innovation_hist, self.nodes[rand_node_1], self.nodes[rand_node_2])
        self.genes.append(ConnectionGene(self.nodes[rand_node_1], self.nodes[rand_node_2], random.uniform(1, -1), conn_inno_num))
        self.connect_nodes()

    def get_innovation_number(self, innovation_hist : list[ConnectionHistory], from_n : Node, to_n : Node):
        """
        Returns innovation number for mutation.\n
        If mutation is new, then a new unique innovation number is assigned.
        Otherwise, find the same innovation number
        """
        is_new = True
        conn_inno_num = Genome.next_conn_num

        for ch in innovation_hist:
            if ch.matches(self, from_n, to_n):
                is_new = False
                conn_inno_num = ch.innovation_num
                break
        
        if is_new:
            inno_nums = []
            for conn in self.genes:
                inno_nums.push(conn.innovation_num)
            
            innovation_hist.append(ConnectionHistory(from_n, to_n, conn_inno_num, inno_nums))
            Genome.next_conn_num += 1
        
        return conn_inno_num

    def mutate(self, innovation_hist : list[ConnectionHistory]):
        """
        Mutates the genome.\n
        80% chance to mutate connection weights\n
        5% chance to add random connection\n
        1% chance to add random node
        """
        if len(self.genes) == 0:
            self.add_connection(innovation_hist)
        
        rand = random.random()
        if rand < 0.8:
            for conn in self.genes:
                conn.mutate_weight()

        rand = random.random()
        if rand < 0.05:
            self.add_connection(innovation_hist)
        
        rand = random.random()
        if rand < 0.01:
            self.add_node(innovation_hist)

    def crossover(self, other_parent):
        """
        Called if this genome is better than other parent. Creates a child genome with mix of genes from another parent.
        """
        child = Genome(self.inputs, self.outputs, True)
        child.genes = []
        child.nodes = []
        child.layers = self.layers
        child.next_node = self.next_node
        child.bias_node = self.bias_node

        child_genes : list[ConnectionGene] = []
        is_enabled = []

        for conn in self.genes:
            set_enabled = True
            other_gene = self.find_matching_gene(other_parent, conn.innovation_num)

            if other_gene != -1:
                if not conn.enabled or not other_parent.genes[other_gene].enabled:
                    if random.random() < 0.75:
                        set_enabled = False
                
                if random.random() < 0.5:
                    child_genes.append(conn)
                else:
                    child_genes.append(other_parent.genes[other_gene])
            else:
                child_genes.append(conn)
                set_enabled = conn.enabled
            
            is_enabled.append(set_enabled)

        for n in self.nodes:
            child.nodes.append(n.clone())
        
        for i, conn in enumerate(child_genes):
            child.genes.append(conn.clone(child.get_node(conn.from_node.num), child.get_node(conn.to_node.num)))
            child.genes[i].enabled = is_enabled[i]

        child.connect_nodes()
        return child

    def find_matching_gene(self, parent, inno):
        for i, conn in enumerate(parent.genes):
            if conn.innovation_num == inno:
                return i
        return -1

    def clone(self):
        clone = Genome(self.inputs, self.outputs, True)

        for n in self.nodes:
            clone.nodes.append(n.clone())

        for conn in self.genes:
            clone.genes.append(conn.clone(clone.get_node(conn.from_node.num), clone.get_node(conn.to_node.num)))

        clone.layers = self.layers
        clone.next_node = self.next_node
        clone.bias_node = self.bias_node
        clone.connect_nodes()

        return clone

        
