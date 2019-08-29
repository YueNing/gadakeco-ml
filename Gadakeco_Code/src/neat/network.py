
import numpy as np
import itertools
import random
import collections

class Network:
    def __init__(self):
        self.fitness = 0
        self._mutate_add_connection()
        self.values = {}
    
    def __str__(self):
        """
            used to print the class Network information
        """
        network = collections.OrderedDict()
        network = self.genome.nodes
        return f"{network}"

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
        if len(self.genome.nodes["input_nodes"]) != len(values):
            raise RuntimeError("Expected {0:n} inputs, got {1:n}".format(len(self.genome.input_nodes), len(values)))
        for k, v in zip(self.genome.nodes["input_nodes"], values):
            self.values[k.node_name] = v
        
        for layer in self.genome.layers[1:-1]:
            for node in layer:
                node_inputs = []
                for i, w in node.links:
                    node_inputs.append(self.values[i] * w)
                s = node.agg_func(node_inputs)
                self.values[node.node_name] = node.act_func(node.bias + node.response * s)
        
        return [self.values[n.node_name] for n in self.genome.nodes["output_nodes"]]
#         return [False, False, False]

class DefaultGenome(object):
    def __init__(self, key):
        self.key = key
        # initial connection, full/none/random
        self.initial_connection = "full"
        self.node_add_prob = 0.1
        self.conn_add_prob = 0.2
        self._set_genome()
    
    def _set_genome(self):

        """
            genome data structur:
                self.layers = [[DefaultNode, DefaultNode, DefaultNode], 
                                [DefaultNode, DefaultNode ,DefaultNode], 
                                [DefaultNode, DefaultNode], 
                                [DefaultNode, DefaultNode, DefaultNode]
                            ]
                
                self.nodes = {"input_nodes":[DefaultNode, DefaultNode, DefaultNode], 
                                "hidden_nodes_{index}":[DefaultNode, DefaultNode, DefaultNode], 
                                        "output_nodes":[DefaultNode, DefaultNode, DefaultNode]
                            }
        """

        self.nodes = collections.OrderedDict()
        self.connection = {}
        self.input_layer_size = 486
        self.hidden_layer_size = [0, 0, 0]
        self.output_layer_size = 3

        self.input_nodes = [DefaultNode(f"in{n}", links=None, act_func='', 
                                agg_func='', bias='', response='') 
                                    for n in range(self.input_layer_size)
                            ]
        self.hidden_nodes = [[DefaultNode(f"h_{l}_{n}") for n in range(l)] for l in self.hidden_layer_size]
        self.output_nodes = [DefaultNode(f"ou{n}") for n in range(3)]

        self.layers = [self.input_nodes]
        for _ in self.hidden_nodes:
            self.layers.append(_)
        self.layers.append(self.output_nodes)

        if self.initial_connection == "full":
            # connection all nodes
            for i in range(len(self.layers)-1):
                for conn in itertools.product(self.layers[i], self.layers[i+1]):
                    self.connection[(conn[0], conn[1])]['weight'] = random.uniform(0, 1)
            
            for layer in self.layers[1:-1]:
                for node in layer:
                    links = []
                    for conn_key in self.connection:
                        inode, onode = conn_key
                        if onode == node:
                            cg = self.connection[conn_key]
                            links.append(inode, cg.weight)
                    node.set_info(links=links)
        
        elif self.initial_connection == "None":
            pass
        
        self.nodes["input_nodes"] = self.layers[0]
        if len(self.layers)>2:
            for index, _ in enumerate(self.layers[1:-2]):
                self.nodes[f"hidden_nodes_{index}"] = _
        self.nodes["output_nodes"] = self.layers[-1]

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

class DefaultNode(object):
    """

        class that used to define the Node information

    """

    def __init__(self, node_name, links=None, act_func='sign', agg_func='sum', bias=0.0, response=1.0):
        self.node_name = node_name
        self.links = links
        if act_func == "sign":
            self.act_func = signmus_activation()
        if agg_func == 'sum':
            self.agg_func = sum
        self.bias = bias
        self.response = response
    
    def set_info(self, links=None, act_func='sign', agg_func='sum', bias=0.0, response=1.0):
        self.links = links
        if act_func == "sign":
            self.act_func = signmus_activation()
        if agg_func == "sum":
            self.agg_func = sum
        self.bias = bias
        self.response = response

    def __str__(self):

        """
            formatt the output of class DefaultNode
        """

        data = {"node_name":self.node_name, "links":self.links, 
                    "act_func":self.act_func, "agg_func":self.agg_func, 
                        "bias":self.bias, "response":self.response
                }
        return f"{data}"

def signmus_activation():
    return lambda x: x and (1, -1)[x < 0]



    
            
