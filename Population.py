import Gene as gn
import Schedule as scdule
import random
import numpy as np

class Population:


    def __init__(self, events) -> None:
        self.events = events
        self.genes = []
        self.calculate_fitness()


    def set_genes(self,genes):
        self.genes = genes
        return self


    def generate(self, size):
        for i in range(0,size):
            self.genes.append(gn.Gene(scdule.generate_schedule(self.events)))
        return self


    def best_fitness(self):
        return self.genes[0].fitness


    def calculate_fitness(self):
        for gene in self.genes:
            gene.calculate_fitness()

    def sort(self):
        self.genes.sort(key=lambda x: x.fitness, reverse=False)

    def elitism(self, elitism_factor):
        elitism_abs = int(len(self.genes)*elitism_factor+1)
        elite = Population(self.events).set_genes(self.genes[:elitism_abs])
        rest = Population(self.events).set_genes(self.genes[elitism_abs:])
        return elite, rest

    def wheel_selection(self, elite_population):
        worst_fitness = self.genes[len(self.genes)-1].fitness
        population = elite_population.genes + self.genes
        fitness_wheel = []
        wheel_total = 0
        for gene in population:
            gen_val = worst_fitness - gene.fitness
            wheel_total += gen_val
            fitness_wheel.append(gen_val)

        p1_raw = random.randint(0, wheel_total)
        p2_raw = random.randint(0, wheel_total)

        p1, p2 = (0, 0)
        while p1_raw > 0:
            p1_raw -= fitness_wheel[p1]
            p1 += 1
        while p2_raw > 0:
            p2_raw -= fitness_wheel[p2]
            p2 += 1

        return p1, p2

    def mate(self, elite_population, selection_type):

        for gene in self.genes:

            p1, p2 = None, None
            # Fully Random
            if selection_type == 0:
                p1, p2 = np.random.choice(elite_population.genes + self.genes, 2)
            # Elitistic Random
            elif selection_type == 1:
                p1, p2 = np.random.choice(elite_population.genes, 2)
            # Wheel Selection
            elif selection_type == 2:
                i1, i2 = self.wheel_selection(elite_population)
                total_pop = elite_population.genes + self.genes
                p1 = total_pop[i1]
                p2 = total_pop[i2]
            # Elitistic Exponential
            elif selection_type == 3:
                i1 = self.generate_idx_exp(len(elite_population.genes + self.genes))
                i2 = self.generate_idx_exp(len(elite_population.genes + self.genes))
                total_pop = elite_population.genes + self.genes
                p1 = total_pop[i1]
                p2 = total_pop[i2]

            # crossover - by events: take some instances from one parent and some from the other
            p1.schedule.instances.sort(key=lambda x: x.title, reverse=True)
            p2.schedule.instances.sort(key=lambda x: x.title, reverse=True)

            instances = list()
            for i in range(0, len(self.events)):
                if random.randint(0, 100) > 50:
                    instances.append(p1.schedule.instances[i])
                else:
                    instances.append(p2.schedule.instances[i])

            gene.set_schedule(scdule.Schedule(instances))

    @staticmethod
    def generate_idx_exp(gen_range):
        prob = random.random()
        max_value = 0
        for i in range(1, gen_range + 1):
            max_value += (1 / 2) ** i
            if prob <= max_value:
                return i - 1
        return Population.generate_idx_exp(gen_range)

    def purge(self, size):
        for i in range(0,size):
            self.genes.pop(0)
        self.generate(size)

    def mutation(self, mutation_rate):
        for gene in self.genes:
            if random.randint(0, 100) < (mutation_rate * 100):
                gene.mutate(self.events)

    @classmethod
    def combine (cls, elite, common):
        population = Population(elite.events)
        population.set_genes(elite.genes)
        population.genes += common.genes
        return population

