from .network import Network     #这为啥报错啊？没毛病啊
import time
import dill as pickle
import gzip
import copy
import random
import logging
import numpy
from scipy import stats

class Population():
    def __init__(self, seed, size=100, initial_state=None):
        """
        Erstellt eine neue Population mit der Groesse 'size' und wird zuerst fuer den uebergebenen seed trainiert.
        """
        self.seed = seed
        self.size = size
        self.repeat_count  = 0
        self.best_network = None
        self.last_best_network = None
        self.selector_probability = list(stats.norm.pdf([i for i in range(self.size)], 0, 1))
        logging.basicConfig(filename='gadakeco.log',level=logging.DEBUG)

        timestr = time.strftime("%d-%m-%y_%H-%M-%S")
        # eindeutiger name name des Netzwerks (noch zu implementieren)
        self.name = f"{timestr}_{self.seed}_{self.size}"

        if initial_state is None:
            # Das Attribut generation_count wird von Gadakeco automatisch inkrementiert. 
            self.generation_count = 1

            self.current_generation = [Network() for _ in range(self.size)]
        else:
            self.generation_count = initial_state[0]
            
            self.current_generation = initial_state[1]

    @staticmethod
    def load_from_file(filename):
        """
        Laedt die komplette Population von der Datei mit dem Pfad filename.
        """
        print("called load_from_file")
        with gzip.open(filename) as f:
            seed, generation_count, current_generation = pickle.load(f)

        return Population(seed, initial_state=(generation_count, current_generation))

    def save_to_file(self, filename):
        """
        Speichert die komplette Population in die Datei mit dem Pfad filename.
        """
        print(f"called save_to_file {self.generation_count}")

        # Save the data
        with gzip.open(filename, 'w', compresslevel=5) as f:
            #data = (self.current_generation, config, population, species_set, random.getstate())   #todo 这啥呀，里面的参数都没定义
            data = (self.seed, self.generation_count, self.current_generation)
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def create_next_generation(self):
        """
        Erstellt die naechste Generation.
        """
        # TODO genomes mutate, crossover
        
        # find the 10% beste individuen, and survive to next step
        survive_size = int(0.1 * self.size)
        mutated_size = int(0.9 * self.size)
        # survive_network = sorted(self.current_generation, key=lambda x: x.fitness, reverse=True)[:survive_size]
        _network = sorted(self.current_generation, key=lambda x: x.fitness, reverse=True)
        
        # check the best 10 generation
        if self.best_network is None:
            self.best_network = copy.deepcopy(_network[0])
        
        if self.last_best_network is None:
            pass
        elif not _network[0].fitness  > 1.001 *self.last_best_network.fitness:
            self.repeat_count +=1
            print(f"repeat no improvement fitness {self.repeat_count} !")
        else:
            self.repeat_count = 0
            print(f'network has improvement !')
        
        self.last_best_network = copy.deepcopy(_network[0])
        
        # if self.best_network.fitness >=  1.1 * _network[0].fitness:
        #     self.repeat_count +=1
        #     print(f"repeat no improvement fitness {self.repeat_count} !")
        
        print(f"_network[0].fitness is {_network[0].fitness} and self.best_network.fitness is {self.best_network.fitness}")
        if _network[0].fitness > self.best_network.fitness:
            self.best_network = copy.deepcopy(_network[0])
            # print(f'best fitness now is {self.best_network.fitness}')

        if self.repeat_count == 100:
            print("Evolution fails, try other evolutionary routes!")
            self.repeat_count = 0
            survive_network = [copy.deepcopy(self.best_network) for i in range(survive_size)]
            self.last_best_network = copy.deepcopy(self.best_network)
            # print(f'repeat count is {self.repeat_count}  and best fitness is {self.best_network.fitness}!')
        else:
            ## base on probability, not just the top 10%
            survive_network = []
            selected_num = 0
            for index, p in enumerate(self.selector_probability):
                if selected_num < survive_size:
                    t = random.random()
                    if p > t:
                        pass
                    else:
                        survive_network.append(_network[index])
                        selected_num +=1
                else:
                    break
            if len(survive_network) == survive_size:
                pass
            else:
                for i in range(survive_size - len(survive_network)):
                    survive_network.append(copy.deepcopy(_network[i]))
        
        # mutation
        used_network = []
        for n in range(int(mutated_size/survive_size)):
            used_network += copy.deepcopy(survive_network) 
        for n in range(mutated_size%survive_size):
            used_network.append(survive_network[n]) 
        # https://www.python-course.eu/python3_deep_copy.php (deepcopy)
        mutated_connection_network = used_network[:int(0.8*len(used_network))]
        mutated_node_network = used_network[-int(0.2*len(used_network)):]
        for n in mutated_connection_network:
            n.genome.mutate_add_connection()
            #调试，加快突变,可能需要一次或多次突变/代
        for n in mutated_node_network:
            n.genome.mutate_add_node()
        self.current_generation = survive_network + mutated_connection_network + mutated_node_network
        random.shuffle(self.current_generation)
        for index, n in enumerate(self.current_generation):
            logging.info(f"generation_{self.generation_count}, network_{index}: {n}")
        
