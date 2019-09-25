from .network import Network     #这为啥报错啊？没毛病啊
import time
import dill as pickle
import gzip
import copy
import random
import logging

class Population():
    def __init__(self, seed, size=100, initial_state=None):
        """
        Erstellt eine neue Population mit der Groesse 'size' und wird zuerst fuer den uebergebenen seed trainiert.
        """
        self.seed = seed
        self.size = size
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
        print("called save_to_file")

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
        survive_network = sorted(self.current_generation, key=lambda x: x.fitness, reverse=True)[:survive_size]
        # survive_network = survive_network + sorted(self.current_generation, key=lambda x: x.fitness, reverse=False)[:int(survive_size * 0.1)]
        
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
            n.genome.mutate_add_connection()
            n.genome.mutate_add_connection()
            n.genome.mutate_add_connection()
            #调试，加快突变
        for n in mutated_node_network:
            n.genome.mutate_add_node()
        self.current_generation = survive_network + mutated_connection_network + mutated_node_network
        random.shuffle(self.current_generation)
        for index, n in enumerate(self.current_generation):
            logging.info(f"generation_{self.generation_count}, network_{index}: {n}")
        
