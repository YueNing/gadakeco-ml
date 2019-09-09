<<<<<<< Updated upstream
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
        
        for layer in self.genome.layers[1:]:
            for node in layer:
                node_inputs = []
                if node.links is not None:
                    for i, w in node.links:
                        node_inputs.append(self.values[i] * w)
                    s = node.agg_func(node_inputs)
                    self.values[node.node_name] = node.act_func(node.bias + node.response * s)
                else:
                    self.values[node.node_name] = None
        # import pdb; pdb.set_trace()
        return [ True if self.values[n.node_name] == 1 else False for n in self.genome.nodes["output_nodes"]]

class DefaultGenome(object):
    def __init__(self, key):
        self.key = key
        # initial connection, full/none/empty/random
        self.initial_connection_type = "full"
        self.node_add_prob = 0.1
        self.conn_add_prob = 0.2
        self._set_genome()
    
    def _convert_to_dict(self, data):
        dict_data = {}
        for k in data:
            if isinstance(k, list):
                dict_data = {**dict_data, **self._convert_to_dict(k)}
            elif isinstance(k, DefaultNode):
                dict_data[k.node_name] = k
        return dict_data
    
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
        self.hidden_layer_size = [6, 4, 4]
        self.output_layer_size = 3

        self.input_nodes = [DefaultNode(f"in{n}", links=None, act_func='', 
                                agg_func='', bias='', response='', node_type="input") 
                                    for n in range(self.input_layer_size)
                            ]
        self.input_nodes_dict = self._convert_to_dict(self.input_nodes)
        self.hidden_nodes = [[DefaultNode(f"h_{l}_{n}", node_type=f"h_{l}") for n in range(l)] for l in self.hidden_layer_size]
        self.hidden_nodes_dict = self._convert_to_dict(self.inputhidden_nodes_nodes)

        self.output_nodes = [DefaultNode(f"ou{n}", node_type="output") for n in range(3)]
        self.output_nodes_dict = self._convert_to_dict(self.output_nodes)
        
        # 将nodes 逐层 添加到layers（list）中，实现上述layer结构
        self.layers = [self.input_nodes]    # [input_layer [nodes]]
        for _ in self.hidden_nodes:     # _ [each layer] from hidden layers
            self.layers.append(_)
        self.layers.append(self.output_nodes)   # [output layer]

        if self.initial_connection_type == "full":
            # connection all nodes
            for i in range(len(self.layers)-1): # other than the output layer
                # 返回前一层node与后一层node的全部排列组合 conn = [node0, node1]
                for conn in itertools.product(self.layers[i], self.layers[i+1]):    # product:返回A、B中的元素的笛卡尔积的元组
                    # full connect, initialize weight of each connect
                    # connection is a {} of Defaultgenome
                    self.connection[(conn[0].node_name, conn[1].node_name)] = {'weight': random.uniform(-1, 1)}

            # asign the connection & weight to nodes
            for layer in self.layers[1:]:   # start from hidden layers
                for node in layer:
                    links = []
                    for conn_key in self.connection:
                        inode, onode = conn_key     # extract data of connection and give them
                        if onode == node.node_name:     # traversal to find the pairing node to asign connection to
                            cg = self.connection[conn_key]
                            links.append((inode, cg["weight"]))     # append () to []
                    node.set_info(links=links)
        elif self.initial_connection_type == "empty":
            for layer in self.layers[1:]:
                for node in layer:
                    links = []
                    self.mutate_add_connection()
        elif self.initial_connection_type == "None":
            pass
        
        self.nodes["input_nodes"] = self.layers[0]
        if len(self.layers)>2:
            for index, _ in enumerate(self.layers[1:-1]):
                self.nodes[f"hidden_nodes_{index}"] = _
        self.nodes["output_nodes"] = self.layers[-1]

    def mutate(self):
        if random.random() < self.node_add_prob:
            self.mutate_add_node()
        if random.random() < self.conn_add_prob:
            self.mutate_add_connection()
    
    # TODO: node mutation (a, b, w) -> (a, c, 1), (c, b, w)
    def mutate_add_node(self):
        
        """
            mutate a node in genome

        """
        # check connection, has connection then can mutate node
        if not self.connection:
            self.mutate_add_connection()
            # ! need to ensure that there are connection of both directions
            return
        
        conn_to_split = random.choice(list(self.connection))
    
    def mutate_add_connection(self, direction):
        '''
        :param direction: 1 = connect to former layer, 0 = to later layer
        #TODO use Uniform distribution or Gauss distribution
        '''
        if direction == 1: # connect to former
            # get the list length of former layer, choose a node to connect

            # check if
        elif direction == 0:    # connect to later

        pass
    
    def mutate_delete_node(self):
        """
            delete a existed node
        """
        pass
    
    def mutate_delete_connection(self):
        """
            delete a connection
        """
        pass

class DefaultNode(object):
    """

        class that used to define the Node information

    """

    def __init__(self, node_name, links=None, act_func='sign', agg_func='sum', bias=0.0, response=1.0, node_type=None):
        self.node_name = node_name
        self.links = links
        self.act_func_name = act_func
        self.agg_func_name = agg_func
        if act_func == "sign":
            self.act_func = signmus_activation()

        if agg_func == 'sum':   # sign 和sum 是作为一个初始标记使用
            self.agg_func = sum
        self.bias = bias
        self.response = response    # ?
        self.node_type = node_type  # 标记输出、输出、隐藏层

    def set_info(self, links=None, act_func='sign', agg_func='sum', bias=0.0, response=1.0):
        self.links = links
        self.act_func_name = act_func
        self.agg_func_name = agg_func
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
                    "act_func":self.act_func_name, "agg_func":self.agg_func_name, 
                        "bias":self.bias, "response":self.response
                }
        return f"{data}"
def signmus_activation():
    return lambda x: x and (1, -1)[x < 0]         


class Network:
    def __init__(self):
        self.fitness = 0

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
        #valuse is the input list, randomly connected to nodes

            #weight_list = random.choices([-1, 0, 1], k=486)
        #github upload test
        return [False, False, False]
