import Gene as gn
import Schedule as scdule
import random
import numpy.random as np

class Population:


    def __init__(self, events) -> None:
        self.events = events
        self.genes = []


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
        return elite,rest


    def mate(self,elite_population):
        for gene in self.genes:

            # TODO - oop design here!

            # selection - from elite population

            self.genes.sort(key=lambda x: x.fitness, reverse=False)
            p1,p2 = np.choice(elite_population.genes,2)

            # crossover - by events: take some instances from one parent and some from the other

            p1.schedule.instances.sort(key=lambda x: x.title, reverse=True)
            p2.schedule.instances.sort(key=lambda x: x.title, reverse=True)

            instances = list()
            for i in range(0, len(self.events)):
                if random.randint(0,100) > 50:
                    instances.append(p1.schedule.instances[i])
                else:
                    instances.append(p2.schedule.instances[i])
            gene.set_schedule(scdule.Schedule(instances))


    def mutation(self, mutation_rate):
        for gene in self.genes:
            if random.randint(0, 100) < (mutation_rate * 100):
                gene.mutate(self.events)

    @classmethod
    def combine (cls,elite,common):
        population = Population(elite.events)
        population.set_genes(elite.genes)
        population.genes += common.genes
        return population

