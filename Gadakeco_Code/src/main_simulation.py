import multiprocessing
import random
from multiprocessing import Pool

from lib import constants
from neat.population import Population
from world import NeuronalWorld
import matplotlib.pyplot as plt
import numpy

hl, = plt.plot([], [])

number_of_processes = min(100, max(multiprocessing.cpu_count() - 2, 1))
pop_name = "30-09-19_17-01-49_976_100"  # ?这个怎么是静态的orz


def evaluate(world):
    while world.update(constants.UPS):
        pass
    return world.nn.fitness


def main():
    try:
        pop = Population.load_from_file(constants.res_loc("networks") + pop_name + ".pop")
    except:
        seed = random.randint(0, 1000)
        pop = Population(seed, 100)

    pool = Pool(number_of_processes)
    while True:
        worlds = []
        for net in pop.current_generation:
            nWorld = NeuronalWorld(pop.seed, net)
            worlds.append(nWorld)
            nWorld.generatePlatform()

        # evaluate all neuronal worlds
        fitnesses = pool.map(evaluate, worlds)
        # set the fitness (because multiprocessing)
        for world, fit in zip(worlds, fitnesses):
            world.nn.fitness = fit

        path = constants.res_loc("networks") + pop.name + ".pop"
        pop.save_to_file(path)
        best_fitness =  max(nn.fitness for nn in pop.current_generation)
        print("best fitness:", best_fitness)
        pop.create_next_generation()
        pop.generation_count += 1

if __name__ == '__main__':
    print("starting simulation with {} processes".format(number_of_processes))
    main()
