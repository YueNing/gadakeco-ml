import numpy as np
import itertools
import random
import collections


class Network:

    def __init__(self):
        self.fitness = 0
        self.genome = DefaultGenome('gadakeco')
        self.values = {}    # save all the values in nodes
        #self._mutate_add_connection() should not be used. mutate_* function only will be called in population.py

    def __str__(self):
        """
            used to print the class Network information
        """
        network =self.genome.input_nodes_list + self.genome.hidden_nodes_list + self.genome.output_nodes_list

        return f"{network}"

    #def _mutate_add_connection(self):  
    #    self.genome.mutate_add_connection()
        
    def update_fitness(self, points, time):
        """
        Berechnet und aktualisiert den Fitness-Wert des Netzwerks 
        basierend auf den Punkten (des 'Spielers') und der vergangenen Zeit.
        """
        self.fitness = points - 50 * time

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
        if sum(input_values) == 0:
            print("warning, the sum of input = 0")
            return
        for k, v in zip(self.genome.input_nodes_dict.keys(), input_values):
            self.values[k] = v
        for node in self.genome.output_nodes_dict.values():
            self.evaluate_node(node)
            # calculate the value of the output_node and save them into self.values list
        return [ True if self.values[node.node_name] > 0.5 else False for n in self.genome.output_nodes_dict.values()]
        # 调试，上述if原本判定为==1

    def evaluate_node(self, node):
        """
        迭代评估每个node的输出，从output向前追溯每层相关的inputnode
        主程序中对每个output调用本函数即可
        """
        if node.node_type=="input":  # ps type数据仅在初始化时有维护
            return
        if node.links is None:
            self.values[node.node_name] = 0 # values是在evaluate时保存输入的图像的字典 key=node_name
            return self.values[node.node_name]

        number_of_links = len(node.links)  # 数据结构：每个node的输入links = [(inputnode, weight),(),()]
        links_with_known_value = 0

        for link in node.links:
            # import pdb; pdb.set_trace()
            if link[0].node_name not in self.values:    # link：[节点，权重]
                self.evaluate_node(link[0]) # 调用函数本身 #todo debug 循环调用出错
                links_with_known_value += 1
            else:
                links_with_known_value += 1

            if links_with_known_value == number_of_links:
                node_inputs = []
                for i, w in node.links:  #todo bug? links 数据结构[()()()]
                    node_inputs.append(self.values[i.node_name] * w)
                suminput = node.agg_func(node_inputs)
                self.values[node.node_name] = node.act_func(node.bias + node.response * suminput)
                #计算出node的value保存在values字典中
                return self.values[node.node_name]


class DefaultGenome(object):
    def __init__(self, key):
        self.key = key
        self.input_layer_size = 486
        self.hidden_layer_size = 10
        self.output_layer_size = 3
        # initial connection: full/none/random/layer # todo: bug when initialize with random connection
        self.initial_connection = "layer"
        self.node_add_prob = 0.3
        self.conn_add_prob = 0.4
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

    def _connect_node_pair(self, node1, node2, mode ='sort'):
        """工具函数，类内部使用
        :parameter mode = sort/simple
        """
        if mode == 'sort':  # 只允许从小id指向大id连接
            if node1.get_node_id() > node2.get_node_id():
                node1, node2 = node2, node1
            elif node1.get_node_id() == node2.get_node_id():
                print(f"warning, same id were given in mode '{mode}' while connecting 2 nodes")
                return
            else:
                pass
        elif mode == 'simple':  # 按给定参数顺序连接
            if node1.get_node_id() == node2.get_node_id():
                print(f"warning, same id were given in mode '{mode}' while connecting 2 nodes")
                return
            else:
                pass
        weight = random.choice([1,-1])
        node2.set_links((node1,weight))

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
        # hidden layer doesn't have further layers anymore
        # all information stored in nodes

        #self.nodes = collections.OrderedDict()
        #self.connection = {}    # not maintained

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

    def mutate_add_node(self, mode='break'):
        # node mutation (a, b, w) -> (a, c, 1), (c, b, w)
        # create a new node in hidden layer
        self.hidden_layer_size += 1
        added_node = DefaultNode(f"h_{self.hidden_layer_size}", node_type=f"hidden")
        self.hidden_nodes_dict['added_node.node_name'] = added_node

        if mode == 'break':   # 破坏一个connection，中间加塞新的node
            # input of chosen node --> added node --> chosen node （random weight
            selected_nodes = []
            for n in self.hidden_nodes_dict.values():
                if not n.links:
                    pass
                else:
                    selected_nodes.append(n)
            chosen_node = random.choice(selected_nodes)
            chosen_inputnode, chosen_weight = random.choice(chosen_node.links)

            added_node.set_links((chosen_inputnode,random.choice([-1,1])))
            chosen_node.set_links((added_node,random.choice([-1,1])))
        else:
            pass

    def mutate_add_connection(self, mode='auto'):
        # TODO: connection mutation, use Uniform distribution or Gauss distribution
        if mode == 'auto':   # random choose from the following modes
            mode = random.choice(['hh', 'ih', 'ho','weight'])    #todo adaptive probability
        elif mode == 'hh':    # hidden --> hidden
            node_a = random.choice(list(self.hidden_nodes_dict.values()))
            node_b = random.choice(list(self.hidden_nodes_dict.values()))
            self._connect_node_pair(node_a, node_b, 'sort')
            print('hh connection added')
        elif mode == 'ih':  # input --> hidden
            node_a = random.choice(list(self.input_nodes_dict.values()))
            node_b = random.choice(list(self.hidden_nodes_dict.values()))
            node_b.set_links((node_a,random.choice([-1, 1])))
        elif mode == 'ho':  # hidden --> output
            node_a = random.choice(list(self.hidden_nodes_dict.values()))
            node_b = random.choice(list(self.output_nodes_dict.values()))
            node_b.set_links((node_a,random.choice([-1, 1])))
        elif mode =='weight':
            weight_change_node = random.choice(list(self.hidden_nodes_dict.values()))
            weight_change_node.set_links((weight_change_node,1) ,mode='weight')
        else:
            print('undefined mode')
            return

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
        if agg_func == 'sum':
            self.agg_func = sum
        self.bias = bias
        self.response = response
        self.node_type = node_type  # 标记输出、输出、隐藏层

    def set_links(self, newlink, mode = 'add'):
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
        return id
    
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

def signmus_activation():
    return lambda x: x and (1, -1)[x < 0]         
