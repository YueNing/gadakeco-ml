from neat.network import Network
import time
import pickle
import gzip

class Population():
    def __init__(self, seed, size, initial_state=None):
        """
        Erstellt eine neue Population mit der Groesse 'size' und wird zuerst fuer den uebergebenen seed trainiert.
        """
        self.seed = seed
        if initial_state is None:
            # Das Attribut generation_count wird von Gadakeco automatisch inkrementiert. 
            self.generation_count = 1

            # eindeutiger name name des Netzwerks (noch zu implementieren)
    #         self.name = "name"
            timestr = time.strftime("%d-%m-%y_%H-%M-%S")
            self.name = timestr

            self.current_generation = [Network() for _ in range(size)]
        else:
            self.generation_count = initial_state[0]
            
            #TODO reproduce the current_generation
            config_current_generation = initial_state[1]

    @staticmethod
    def load_from_file(filename):
        """
        Laedt die komplette Population von der Datei mit dem Pfad filename.
        """
        print("called load_from_file")
        with gzip.open(filename) as f:
            seed, generation_count, config_current_generation = pickle.load(f)
        return Population(seed, 100, (generation_count, config_current_generation))

    def save_to_file(self, filename):
        """
        Speichert die komplette Population in die Datei mit dem Pfad filename.
        """
        print("called save_to_file")
        print(filename)
        # TODO get the config of current generation
        self.config_current_generation = {("inode", "onode"):{"weight":1}, }
        # Save the data
        with gzip.open(filename, 'w', compresslevel=5) as f:
#             data = (self.current_generation, config, population, species_set, random.getstate())
            data = (self.seed, self.generation_count, self.name , self.config_current_generation)
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def create_next_generation(self):
        """
        Erstellt die naechste Generation.
        """
        # TODO genomes mutate, crossover
        self.current_generation = []
        
