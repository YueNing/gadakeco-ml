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
        # for layer in self.genome.layers[1:]:
        #     for node in layer:
        #         node_inputs = []
        #         if node.links is not None:
        #             for i, w in node.links:
        #                 node_inputs.append(self.values[i] * w)
        #             s = node.agg_func(node_inputs)
        #             self.values[node.node_name] = node.act_func(node.bias + node.response * s)
        #         else:
        #             self.values[node.node_name] = None
        # import pdb; pdb.set_trace()
        for n in self.genome.nodes["output_nodes"]:
            self.evaluate_node(n)
        return [ True if self.values[n.node_name] == 1 else False for n in self.genome.nodes["output_nodes"]]

    def evaluate_node(self, node):
        if node.node_type=="input":
            return
        # print(node.node_name)
        number_of_links       =len(node.links)
        links_with_known_value=0
        if node.links is None:
            self.values[node.node_name] =0
            return self.values[node.node_name]
        for link in node.links:
            # import pdb; pdb.set_trace()
            if link[0].node_name not in self.values:
                self.evaluate_node(link[0])
                links_with_known_value+=1
            else:
                links_with_known_value+=1
        if links_with_known_value==number_of_links:
            node_inputs = []
            for i, w in node.links:
                node_inputs.append(self.values[i.node_name] * w)
            s = node.agg_func(node_inputs)
            self.values[node.node_name] = node.act_func(node.bias + node.response * s)
            return  self.values[node.node_name]
        # print(self.values)
            


class DefaultGenome(object):
    def __init__(self, key):
        self.key = key
        # initial connection, full/none/random
        self.initial_connection = "full"
        self.node_add_prob = 0.1
        self.conn_add_prob = 0.2
        self._set_genome()
    
    def _convert_to_dict(self, data):
        """
            :param: data, type is list, the layer of list is not matter
            return:  dict
            >>> _convert_to_dict([DefaultNode, DefaultNode, DefaultNode])
            >>> {"DefaultNode.node_name":DefaultNode, "DefaultNode.node_name":DefaultNode,  "DefaultNode.node_name":DefaultNode}
            >>> _convert_to_dict([[DefaultNode, DefaultNode, DefaultNode], [DefaultNode, DefaultNode, DefaultNode], [DefaultNode, DefaultNode, DefaultNode]])
            >>> {"DefaultNode.node_name":DefaultNode, "DefaultNode.node_name":DefaultNode,  "DefaultNode.node_name":DefaultNode, 
                        "DefaultNode.node_name":DefaultNode, "DefaultNode.node_name":DefaultNode,  "DefaultNode.node_name":DefaultNode,
                        "DefaultNode.node_name":DefaultNode, "DefaultNode.node_name":DefaultNode,  "DefaultNode.node_name":DefaultNode
                    }
        """
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
        self.hidden_layer_size = [1]
        self.output_layer_size = 3

        # 各层初始化，实现上述nodes结构
        self.input_nodes = [DefaultNode(f"in{n}", links=None, act_func='',  # 第一个参数是node_name，显示为in1 in2……
                                agg_func='', bias='', response='', node_type="input") 
                                    for n in range(self.input_layer_size)
                            ]
        self.input_nodes_dict = self._convert_to_dict(self.input_nodes)
        self.hidden_nodes = [[DefaultNode(f"h_{index}_{n+1}", node_type=f"h_{index}") for n in range(l)] for index, l in enumerate(self.hidden_layer_size)]
        self.hidden_nodes_dict = self._convert_to_dict(self.hidden_nodes)
        self.output_nodes = [DefaultNode(f"ou{n}", node_type="output") for n in range(3)]
        self.output_nodes_dict = self._convert_to_dict(self.output_nodes)

        #将nodes 逐层 添加到layers（list）中，实现上述layer结构
        self.layers = [self.input_nodes]
        for _ in self.hidden_nodes:
            self.layers.append(_)
        self.layers.append(self.output_nodes)

        if self.initial_connection == "full":
            # connection all nodes
            for i in range(len(self.layers)-1):
                for conn in itertools.product(self.layers[i], self.layers[i+1]):
                    self.connection[(conn[0], conn[1])] = {'weight':random.uniform(-1, 1)}
            # import pdb; pdb.set_trace()
            for layer in self.layers[1:]:
                for node in layer:
                    links = []
                    for conn_key in self.connection:
                        inode, onode = conn_key
                        if onode.node_name == node.node_name:
                            cg = self.connection[conn_key]
                            links.append((inode, cg["weight"]))
                    node.set_info(links=links)
            # import pdb;pdb.set_trace()
        
        elif self.initial_connection == "None":
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
            return
        
        conn_to_split = random.choice(list(self.connection))
    
    def mutate_add_connection(self):
        # TODO: connection mutation, use Uniform distribution or Gauss distribution
        temp_list = []
        for h in self.hidden_nodes:
            temp_list += h
        in_node  =random.choice(self.input_nodes+temp_list)
        out_node =random.choice(self.output_nodes+temp_list)

        # import pdb; pdb.set_trace()
        key =(in_node.node_name, out_node.node_name)
        
        if key in self.connection:
            return  
        
        if self.creates_cycle(list(self.connection), (in_node,out_node)):
            return

        self.connection[key] = {'weight':random.uniform(-1, 1)}
        
        
    
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
    
    @staticmethod
    def creates_cycle(connections, test):
        """
        Returns true if the addition of the 'test' connection would create a cycle,
        assuming that no cycle already exists in the graph represented by 'connections'.
        """
        i, o = test
        if i == o:
            return True
    
        visited = {o}
        while True:
            num_added = 0
            for a, b in connections:
                if a in visited and b not in visited:
                    if b == i:
                        return True

                    visited.add(b)
                    num_added += 1

            if num_added == 0:
                return False

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
        if agg_func == 'sum':   # sign 和sum 是作为一个初始标记使用？
            self.agg_func = sum
        self.bias = bias
        self.response = response    # 作用未知
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
        return f"{data}"    # https://cito.github.io/blog/f-strings/

def signmus_activation():
    return lambda x: x and (1, -1)[x < 0]         
