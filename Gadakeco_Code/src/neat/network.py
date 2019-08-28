
import numpy as np
import itertools
import random

class Network:
    def __init__(self):
        self.fitness = 0
        self._mutate_add_connection()
        self.values = {}
    
    def _mutate_add_connection(self):
        self.genome = DefaultGenome('gadakeco')
        self.genome.mutate_add_connection()
        
    def update_fitness(self, points, time):
        """
        Berechnet und aktualisiert den Fitness-Wert des Netzwerks 
        basierend auf den Punkten (des 'Spielers') und der vergangenen Zeit.
        """
        self.fitness = points - 50 * time

    def evaluate(self, values):
        """
        Wertet das Netzwerk aus. 
        
        Argumente:
            values: eine Liste von 27x18 = 486 Werten, welche die aktuelle diskrete Spielsituation darstellen
                    die Werte haben folgende Bedeutung:
                     1 steht fuer begehbaren Block
                    -1 steht fuer einen Gegner
                     0 leerer Raum
        Rueckgabewert:
            Eine Liste [a, b, c] aus 3 Boolean, welche angeben:
                a, ob die Taste "nach Links" gedrueckt ist
                b, ob die Taste "nach Rechts" gedrueckt ist
                c, ob die Taste "springen" gedrueckt ist.
        """
        if len(self.genome.input_nodes) != len(values):
            raise RuntimeError("Expected {0:n} inputs, got {1:n}".format(len(self.genome.input_nodes), len(values)))
        for k, v in zip(self.genome.input_nodes, values):
            self.values[k] = v
        for node, act_func, agg_func, bias, response, links in self.genome.node_evals:
            node_inputs = []
            for i, w in links:
                node_inputs.append(self.values[i] * w)
            s = agg_func(node_inputs)
            self.values[node] = act_func(bias + response * s)
        return [self.values[i] for i in self.genome.output_nodes]
#         return [False, False, False]

class DefaultGenome(object):
    def __init__(self, key):
        self.key = key
        self.connections = {}
        self.nodes = {}
        self.input_nodes = [f'in{i}' for i in range(486)]
        self.hidden_nodes = []
        self.output_nodes = ['links', 'rechts', 'springen']
        self.node_evals = []
        self.fitness = None
        self.initial_connection = "full"
        self.node_add_prob = 0.1
        self.conn_add_prob = 0.2
        self.single_structural_mutation = True
        
        # create a genome
        self._configure()
        
    def _configure(self):
        """
         return:
         [(node, act_func, agg_func, bias, response, links),
         (node, act_func, agg_func, bias, response, links)]
        """
        # get the layers
        layers = [self.input_nodes]
        for _ in self.hidden_nodes:
            layers.append(_)
        layers.append(self.output_nodes)
        
        if self.initial_connection == 'full':
            # get the connections
            for i in range(len(layers) -1):
                for c in itertools.product(layers[i], layers[i+1]):
                    self.connections[(c[0], c[1])]['weight'] = random.uniform(0, 1)
            
            for layer in layers:
                for node in layer:
                    links = []
                    for conn_key in self.connections:
                        inode, onode = conn_key
                        if onode == node:
                            cg = self.connections[(c[0], c[1])]
                            links.append((inode, cg.weight))
                    self.node_evals.append(node, signmus_activation(), sum, 0.0, 1.0, links)
    
    def mutate(self):
        if random.random() < self.node_add_prob:
            self.mutate_add_node()
        if random.random() < self.conn_add_prob:
            self.mutate_add_connection()
    
    def mutate_add_node(self):
        # conn_to_split = 
        # TODO: node mutation (a, b, w) -> (a, c, 1), (c, b, w)
        pass
    
    def mutate_add_connection(self):
        # TODO: connection mutation, use Uniform distribution or Gauss distribution 
        pass

def signmus_activation():
    return lambda x: x and (1, -1)[x < 0]



    
            
