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
            raise RuntimeError("Expected {0:n} inputs, got {1:n}".format(len(self.genome.input_nodes_list), len(values)))
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
        number_of_links =len(node.links)
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
    
    def _set_genome(self):
        # hidden layer doesn't have further layers anymore
        # all information stored in nodes

        self.nodes = collections.OrderedDict()
        self.connection = {}    # not maintained
        self.input_layer_size = 486
        self.hidden_layer_size = 200  # TODO converted form [] to int, need to adjust other parts
        self.output_layer_size = 3

        self.input_nodes_list = [DefaultNode(f"in{n}", links=None, node_type="input")
                                 for n in range(self.input_layer_size)]
        self.hidden_nodes_list = [DefaultNode(f"h_{n + 1}", node_type=f"hidden")
                                  for n in range(self.hidden_layer_size)]
        self.output_nodes_list = [DefaultNode(f"ou{n}", node_type="output")
                                  for n in range(self.output_layer_size)]
        # convert to dictionary, the lists above are temp parameters
        # dictionary structure = {"DefaultNode.node_name":DefaultNode, , }
        self.input_nodes_dict = self._convert_to_dict(self.input_nodes_list)
        self.hidden_nodes_dict = self._convert_to_dict(self.hidden_nodes_list)
        self.output_nodes_dict = self._convert_to_dict(self.output_nodes_list)

        if self.initial_connection == "full":
            # connection all nodes
            self.int_connection_each()
        
        elif self.initial_connection == "None":
            pass
        
        self.nodes["input_nodes"] = self.layers[0]
        if len(self.layers) > 2:
            for index, _ in enumerate(self.layers[1:-1]):
                self.nodes[f"hidden_nodes_{index}"] = _
        self.nodes["output_nodes"] = self.layers[-1]

    def mutate(self):
        if random.random() < self.node_add_prob:
            self.mutate_add_node()
        if random.random() < self.conn_add_prob:
            self.mutate_add_connection()
    
    # TODO: node mutation (a, b, w) -> (a, c, 1), (c, b, w)
    def mutate_add_node(self, mode = 'break'):
        # create a new node in hidden layer
        self.hidden_layer_size += 1
        added_node = DefaultNode(f"h_{self.hidden_layer_size}", node_type=f"hidden")
        self.hidden_nodes_dict['added_node.node_name'] = added_node

        if mode == 'break':   # 破坏一个connection，中间加塞新的node
            # input of chosen node --> added node --> chosen node （random weight）
            chosen_node = random.choice(self.hidden_nodes_dict.values())
            chosen_inputnode, chosen_weight = random.choice(chosen_node.links)

            added_node.set_links(chosen_inputnode,random.choice([-1,1]))
            chosen_node.set_links(added_node,random.choice([-1,1]))
        else:
            pass
        '''
        # the connection parameter below is no longer maintained
        if not self.connection:
            self.mutate_add_connection()
            return
        conn_to_split = random.choice(list(self.connection))
        '''

    def int_connection_each(self):
        '''

        each hidden node has 1 connection to input, and 1 to output

        '''
        temp_list = []
        for h in self.hidden_nodes_list:
            temp_list += h
        in_node  =random.choice(self.input_nodes_list + temp_list)
        out_node =random.choice(self.output_nodes_list + temp_list)

        # add connect_info to nodes, random weight
        self.connect_node_pair(in_node,out_node,'simple')

        # import pdb; pdb.set_trace()
        key =(in_node.node_name, out_node.node_name)

        if key in self.connection:
            return  
        
        if self.creates_cycle(list(self.connection), (in_node, out_node)):
            return

        self.connection[key] = {'weight':random.uniform(-1, 1)}


    def connect_node_pair(self, node1, node2, mode = 'sort'):
        if mode == 'sort':  # 只允许从小id指向大id连接
            if node1.get_node_id > node2.get_node_id:
                node1, node2 = node2, node1
            elif node1.get_node_id == node2.get_node_id:
                print("error, same id were given")
            else:
                pass
        elif mode == 'simple':  # 按给定参数顺序连接
            if node1.get_node_id == node2.get_node_id:
                print("error, same id were given")
            else:
                pass
            pass
        weight = random.choice([1,-1])
        node2.set_links((node1,weight))

    def mutate_add_connection(self, mode = 'hh'):
        # TODO: connection mutation, use Uniform distribution or Gauss distribution
        if mode == 'hh':    # hidden --> hidden
            node_a = random.choice(self.hidden_nodes_dict.values())
            node_b = random.choice(self.hidden_nodes_dict.values())
            self.connect_node_pair(node_a,node_b, 'sort')
        elif mode == 'ih':  # input --> hidden
            node_a = random.choice(self.input_nodes_dict.values())
            node_b = random.choice(self.hidden_nodes_dict.values())
            node_b.set_links(node_a,random.choice([-1, 1]))
        elif mode == 'ho':  # hidden --> output
            node_a = random.choice(self.hidden_nodes_dict.values())
            node_b = random.choice(self.output_nodes_dict.values())
            node_b.set_links(node_a,random.choice([-1, 1]))

    def mutate_delete_node(self):

        # input和output都是固定的，所以这里只可能删除hidden node
        delete_node = random.choice(self.hidden_nodes_dict.values())
        delete_name = delete_node.node_name
        self.hidden_nodes_dict.pop('delete_name')

        # 谁把这个node作为input，谁的links就需要更新, 这不涉及input layer
        self.mutate_delete_connection(delete_name)

    def mutate_delete_connection(self, input_node_to_delete):
        delete_name = input_node_to_delete
        for keynode_o in self.output_nodes_dict.item():
            key, value_temp = keynode_o
            if 'delete_name,1' or 'delete_name,-1' in value_temp.links:
                del self.output_nodes_dict['key']
            else:
                pass

        for keynode_h in self.hidden_nodes_dict.item():
            key, value_temp = keynode_h
            if 'delete_name,1' or 'delete_name,-1' in value_temp.links:
                del self.hidden_nodes_dict['key']
            else:
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
        if links == None:
            self.links = []  # [(inputnode, weight),(),()]
        else:
            self.links = links
        self.act_func_name = act_func
        self.agg_func_name = agg_func
        if act_func == "sign":
            self.act_func = signmus_activation()
        if agg_func == 'sum':   # sign 和sum 是作为一个初始标记使用？
            self.agg_func = sum
        self.bias = bias
        self.response = response
        self.node_type = node_type  # 标记输出、输出、隐藏层
    
    def set_links(self, newlink):
        if type(newlink) == list:   # [(inputnode, weight),(),()]
            self.links.extend(newlink)
        elif type(newlink) == tuple:    # (inputnode, weight)
            self.links.append(newlink)
        else:
            print("error! input should be [(inputnode, weight),(),()] or (inputnode, weight)")

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
