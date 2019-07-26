from neat.network import Network


class Population():
    def __init__(self, seed, size):
        """
        Erstellt eine neue Population mit der Groesse 'size' und wird zuerst fuer den uebergebenen seed trainiert.
        """
        self.seed = seed
        # Das Attribut generation_count wird von Gadakeco automatisch inkrementiert. 
        self.generation_count = 1

        # eindeutiger name name des Netzwerks (noch zu implementieren)
        self.name = "name"

        self.current_generation = [Network()]

    @staticmethod
    def load_from_file(filename):
        """
        Laedt die komplette Population von der Datei mit dem Pfad filename.
        """
        print("called load_from_file")
        return None

    def save_to_file(self, filename):
        """
        Speichert die komplette Population in die Datei mit dem Pfad filename.
        """
        print("called save_to_file")

    def create_next_generation(self):
        """
        Erstellt die naechste Generation.
        """
