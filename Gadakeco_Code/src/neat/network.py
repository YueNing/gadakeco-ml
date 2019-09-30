import numpy as np
import itertools
import random
import collections

import yaml
import os
from functools import partial

with open('neat/yconfig.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    print(config)

class Network:

    def __init__(self):
        self.fitness = 0
        self.genome = DefaultGenome('gadakeco')
        self.values = {}    # save all the values in nodes
        #self._mutate_add_connection() should not be used. mutate_* function only will be called in population.py

    def update_fitness(self, points, time):
        """
        Berechnet und aktualisiert den Fitness-Wert des Netzwerks 
        basierend auf den Punkten (des 'Spielers') und der vergangenen Zeit.
        """
        link_count = 0
        for node in self.genome.hidden_nodes_dict.values():
            for link in node.links:
                link_count+=1
        for  node in self.genome.output_nodes_dict.values():
            for link in node.links:
                link_count+=1
        self.fitness = points - 50 * time - 10*len(self.genome.hidden_nodes_dict) - 2*link_count
        # self.fitness = points - 50 * time

    def evaluate(self, input_values):
        """
        Wertet das Netzwerk aus. 
        
        Argumente:
            input_values: eine Liste von 27x18 = 486 Werten, welche die aktuelle diskrete Spielsituation darstellen
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
        if len(self.genome.input_nodes_dict) != len(input_values):
            raise RuntimeError("Expected {0:n} inputs, got {1:n}".format(len(self.genome.input_nodes_list), len(input_values)))
        for k, v in zip(self.genome.input_nodes_dict.keys(), input_values):
            self.values[k] = v

        self.evaluate_hidden_node()
        for node in self.genome.output_nodes_dict.values():
            self.evaluate_output_node(node)
            # calculate the value of the output_node and save them into self.values list
        result = [ True if self.values[n.node_name] > 0.5 else False for n in self.genome.output_nodes_dict.values()]
        self.values = {}
        return result

    def evaluate_output_node(self, node):
        """
            used for evaluate output nodes
        """
        if not node.links:
            self.values[node.node_name] =0 
        else:
            node_inputs = []
            for i, w in node.links:  #todo bug? links 数据结构[()()()]
                node_inputs.append(self.values[i.node_name] * w)
            suminput = node.agg_func(node_inputs)
            self.values[node.node_name] = node.act_func(node.bias + node.response * suminput)

    def evaluate_hidden_node(self):
        """
            used for evaluate the hidden nodes
        """
        for _ in range(len(self.genome.hidden_nodes_dict)):
            for node in self.genome.hidden_nodes_dict.values():
                if node.node_name in self.values:
                    pass
                else:
                    tag = True
                    for link in node.links:
                        if link[0].node_name not in self.values:
                            tag = False
                    if tag:
                        node_inputs = []
                        for i, w in node.links:  #todo bug? links 数据结构[()()()]
                            node_inputs.append(self.values[i.node_name] * w)
                        suminput = node.agg_func(node_inputs)
                        self.values[node.node_name] = node.act_func(node.bias + node.response * suminput)
        
        for node in self.genome.hidden_nodes_dict.values():
            if node.node_name not in self.values:
                self.values[node.node_name] = 0

class DefaultGenome(object):
    def __init__(self, key):
        self.key = key
        self.input_layer_size = 486
        self.hidden_layer_size = config['hidden_layer_size']
        self.output_layer_size = 3
        # initial connection: full/none/random/layer
        self.initial_connection = config['initial_connection']
        self.node_add_prob = config['node_add_prob']
        self.conn_add_prob = config['conn_add_prob']
        self._set_genome()

    def __str__(self):
        return f'DefaultGenome Class: hidden_layer_size={len(self.hidden_nodes_dict)}'
    
    def _convert_to_dict(self, data):
        """
            :param: data, type is list, the layer of list is not matter
            return:  dict
            >>> _convert_to_dict([DefaultNode, DefaultNode, DefaultNode])
            >>> {"DefaultNode.node_name":DefaultNode, , }
            >>> _convert_to_dict([[DefaultNode, DefaultNode, DefaultNode], ,])
            >>> {"DefaultNode.node_name":DefaultNode, , }
        """
        dict_data = {}
        for k in data:
            if isinstance(k, list):
                dict_data = {**dict_data, **self._convert_to_dict(k)}
            elif isinstance(k, DefaultNode):
                dict_data[k.node_name] = k
        return dict_data

    def _connect_node_pair(self, node1, node2, mode ='simple'):
        """工具函数，类内部使用,保证hidden layer的从小到大连接
        :parameter mode = sort/simple
        """
        if mode == 'sort':  # 只允许从小id指向大id连接
            if node1.get_node_id() > node2.get_node_id():
                node1, node2 = node2, node1
            elif node1.get_node_id() == node2.get_node_id():
                # print(f"warning, same id were given in mode '{mode}' while connecting 2 nodes")
                return False
            else:
                pass
        elif mode == 'simple':  # 按给定参数顺序连接
            if node1.get_node_id() == node2.get_node_id():
                # print(f"warning, same id were given in mode '{mode}' while connecting 2 nodes")
                return False
            elif (node1.node_name, node2.node_name) in self.connections:
                return False
            else:
                tag = self.creates_cycle(list(self.connections), (node1.node_name,node2.node_name))
                if tag:
                    return False
                else:
                    weight = random.choice([1,-1])
                    node2.set_links((node1,weight))
                    self.connections[(node1.node_name, node2.node_name)] = weight
                    return True

    def _connect_node_full_init(self, prelayer, thislayer, nextlayer, mode ='full'):
        """
        类内工具，向前向后层进行全连接
        :param：需要输入字典， 比如self.input_nodes_dict
        mode = full/pre/next
        """
        if mode == 'full':
            for hidden_node1 in thislayer.values():
                for input_node_name in prelayer:
                    hidden_node1.set_links((prelayer[input_node_name], random.choice([-1, 1])))
                for output_node in nextlayer.values():
                    output_node.set_links((hidden_node1, random.choice([-1, 1])))
        elif mode == 'pre':
            for hidden_node1 in thislayer.values():
                for input_node_name in prelayer:
                    hidden_node1.set_links((prelayer[input_node_name], random.choice([-1, 1])))
        elif mode == 'next':
            for hidden_node1 in thislayer.values():
                for output_node in nextlayer.values():
                    output_node.set_links((hidden_node1, random.choice([-1, 1])))
        else:
            print('undefined mode in function _connect_node_full_init')
            return
    
    def _set_genome(self):

        self.input_nodes_list = [DefaultNode(f"in_{n}", node_type="input")
                                 for n in range(self.input_layer_size)]
        self.hidden_nodes_list = [DefaultNode(f"h_{n + 1}", node_type="hidden")
                                  for n in range(self.hidden_layer_size)]
        self.output_nodes_list = [DefaultNode(f"out_{n}", node_type="output")
                                  for n in range(self.output_layer_size)]
        # convert to dictionary, the lists above are temp parameters
        # dictionary structure = {"DefaultNode.node_name":DefaultNode, , }
        self.input_nodes_dict = self._convert_to_dict(self.input_nodes_list)
        self.hidden_nodes_dict = self._convert_to_dict(self.hidden_nodes_list)
        self.output_nodes_dict = self._convert_to_dict(self.output_nodes_list)
        self.get_connections()        

        if self.initial_connection == "full":
            #full connect input-->hidden, full connect hidden-->output
            # //i.e. one layer of hidden as initial

            for hidden_node1 in self.hidden_nodes_dict.values():
                for input_node_name in self.input_nodes_dict:
                    hidden_node1.set_links((self.input_nodes_dict[input_node_name], random.choice([-1, 1])))
                for output_node in self.output_nodes_dict.values():
                    output_node.set_links((hidden_node1, random.choice([-1, 1])))

            #self._connect_node_full_init(self.input_nodes_dict, self.hidden_nodes_dict, self.output_nodes_dict)

        elif self.initial_connection =="random":
            #use add_connection mutation to initialize the network\
            for i in range (self.hidden_layer_size):   #todo 不能保证有input-output的通路，在evaluate时有bug
                self.mutate_add_connection(mode='ih')
                self.mutate_add_connection(mode='ho')
                self.mutate_add_connection(mode='hh')
                self.mutate_add_connection(mode='auto')

        elif self.initial_connection == "layer":
            layer_dict1 = {}
            layer_dict2 = {}
            for hidden_node in self.hidden_nodes_dict.keys():
                temp, id_int = hidden_node.split("_")

                if int(id_int) < self.hidden_layer_size:
                    layer_dict1[hidden_node] = self.hidden_nodes_dict[hidden_node]
                else:
                    layer_dict2[hidden_node] = self.hidden_nodes_dict[hidden_node]
            self._connect_node_full_init(self.input_nodes_dict, layer_dict1, layer_dict2)
            self._connect_node_full_init(layer_dict1, layer_dict2, self.output_nodes_dict, mode='next')
        elif self.initial_connection == "None":
            print("Error! undefined keyword was given in initializing")

    def get_connections(self):
        self.connections = {}
        for node in {**self.hidden_nodes_dict, **self.output_nodes_dict}.values():
            for link in node.links:
                in_node = link[0].node_name
                out_node = node.node_name
                self.connections[(in_node, out_node)] = link[1]
        # print(f'initial connections {self.connections}')

    def mutate_connection(self):
        if random.random() < self.conn_add_prob:
            self.mutate_add_connection()
        else:
            self.mutate_delete_connection()

    def mutate_node(self):
        if random.random() < self.node_add_prob:
            self.mutate_add_node()
        else:
            self.mutate_delete_node()

    def mutate_add_node(self,mode='break'):
        """
            ode mutation (a, b, w) -> (a, c, 1), (c, b, w)
            create a new node in hidden layer
        """
        # register the added node in dict
        self.hidden_layer_size += 1
        added_node = DefaultNode(f"h_{self.hidden_layer_size}", node_type="hidden")
        self.hidden_nodes_dict[added_node.node_name] = added_node

        if mode == 'simple':
            # print(f'{added_node.node_name} added without connection')
            return
        elif mode == 'break':  # todo bug:break模式会导致添加node后connection的id不再单向递增
            selected_nodes = []
            for n in self.hidden_nodes_dict.values():
                # print(f'{n.node_name} links are {n.links}!')
                if not n.links:
                    pass
                else:
                    selected_nodes.append(n)
            if not selected_nodes:
                pass
            else:
                chosen_node = random.choice(selected_nodes)
                chosen_inputnode, chosen_weight = random.choice(chosen_node.links)

                weight1 = random.choice([-1,1])
                weight2 = random.choice([-1,1])
                added_node.set_links((chosen_inputnode,weight1))
                chosen_node.set_links((added_node,weight2))
                self.connections[(chosen_inputnode.node_name, added_node.node_name)] = weight1
                self.connections[(added_node.node_name, chosen_node.node_name)] = weight2                 
                # print(f'added_node: {added_node.node_name}->choosed_node: {chosen_node.node_name}')
        # print(f'mutated add node connections {self.connections}')
        
    def mutate_add_connection(self, mode='auto'):
        if mode == "auto":  # adaptive probability: edit the weights below
            weight_config = config['mutate_add_connection_weights']
            mode = random.choices(population=['ih', 'hh', 'ho'], weights=weight_config)[0]
        if mode == 'hh':    # hidden --> hidden
            # not successful added connection
            tag = False
            try_count = 0
            while not tag and try_count<10:
                node_a = random.choice(list(self.hidden_nodes_dict.values()))
                node_b = random.choice(list(self.hidden_nodes_dict.values()))
                tag = self._connect_node_pair(node_a, node_b, 'simple')
                try_count += 1
                # print(f'{node_a} and {node_b}:{node_a.node_name} --> {node_b.node_name} hh connection added {node_a.links} and {node_b.links}')
                # print(f'connection added {node_a.node_name} -> {node_b.node_name} !')        
        elif mode == 'ih':  # input --> hidden
            # Use gaussian distribution here, not just random
            tag = True
            try_count = 0
            while tag and try_count<10:
                mean = [11, 10]
                cov = [[27.0/2, 0], [0, 9]]
                x, y = np.random.multivariate_normal(mean, cov)
                id = (int(x) + int(y)*27) % (27*18)
                # print(f'id is {id} x and y is {x} {y}')
                node_a = self.input_nodes_list[id]
                node_b = random.choice(list(self.hidden_nodes_dict.values()))
                if (node_a.node_name, node_b.node_name) not in self.connections:
                    weight = random.choice([-1, 1])
                    node_b.set_links((node_a,weight))
                    self.connections[(node_a.node_name, node_b.node_name)] = weight
                    tag = False
                try_count+=1
        elif mode == 'ho':  # hidden --> output
            tag = True
            try_count = 0
            while tag and try_count<10:
                node_a = random.choice(list(self.hidden_nodes_dict.values()))
                node_b = random.choice(list(self.output_nodes_dict.values()))
                weight = random.choice([-1, 1])
                if (node_a.node_name, node_b.node_name) not in self.connections:
                    node_b.set_links((node_a,weight))
                    self.connections[(node_a.node_name, node_b.node_name)] = weight      
                    tag = False      
                try_count += 1
        else:
            print(f'undefined mode = {mode}')
            return
    
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

    def mutate_delete_node(self):
        """
            random to delete a node in network, and update relate connections in self.connetions
        """

        # input和output都是固定的，所以这里只可能删除hidden node
        if self.hidden_nodes_dict:
            delete_node = random.choice(list(self.hidden_nodes_dict.values()))
            delete_name = delete_node.node_name
            
            for k in list(self.connections):
                if delete_name in k:
                    in_node, out_node = k
                    if in_node == delete_name:
                        node = self.get_node_class(out_node)
                        for index, link in enumerate(node.links):
                            if link[0].node_name == in_node:
                                del node.links[index]
                                break
                    del self.connections[k]

            del self.hidden_nodes_dict[delete_name]

    def get_node_class(self, node_name):
        """
            return a instance of Node
        """
        for node in {**self.hidden_nodes_dict, **self.output_nodes_dict}.values():
            if node.node_name == node_name:
                return node

    def mutate_delete_connection(self):
        """
            random to delete a connection in network, and update connection in relate node
        """
        if self.connections:
            key = random.choice(list(self.connections.keys()))
            in_node, out_node = key
            del self.connections[key]
            node = self.get_node_class(out_node)
            for index, link in enumerate(node.links):
                if link[0].node_name == in_node:
                    del node.links[index]
                    break


class DefaultNode(object):
    """

        class that used to define the Node information

    """

    def __init__(self, node_name, links=None, act_func='sign', agg_func='sum', bias=0.0, response=1.0, node_type=None):
        self.node_name = node_name
        if links == None:
            self.links = []  # [(inputnode, weight),(),()]
        else:
            self.links = links
        self.act_func_name = act_func
        self.agg_func_name = agg_func
        if act_func == "sign":
            self.act_func = np.sign
        if agg_func == 'sum':
            self.agg_func = sum
        self.bias = bias
        self.response = response
        self.node_type = node_type  # 标记输出、输出、隐藏层

    def set_links(self, newlink, mode='add'):
        if mode == 'add':
            if type(newlink) == list:   # [(inputnode, weight),(),()]
                self.links.extend(newlink)
            elif type(newlink) == tuple:    # (inputnode, weight)
                self.links.append(newlink)
            else:
                print("error! input should be [(inputnode, weight),(),()] or (inputnode, weight)")
        elif mode == 'weight':  # 该点的每个input connection的权重突变
            temp_links = []
            for inputnode, weight in self.links:
                temp_links.append((inputnode,random.choice([-1,1])))
            self.links = temp_links
        else:
            print('undefined mode')

    def get_node_id(self):
        type, id =self.node_name.split("_")
        #print(type,id, self.node_name)
        return int(id)
    
    def get_node_name(self):
        return self.node_name
    
    def __str__(self):

        """
            formatt the output of class DefaultNode
        """

        data = {"node_name":self.node_name, "links":self.links, 
                    "act_func":self.act_func_name, "agg_func":self.agg_func_name, 
                        "bias":self.bias, "response":self.response
                }
        return f"{data}"    # https://cito.github.io/blog/f-strings/