from abc import ABC

import math
import random

import Schedule as scdule
import Population as pop

class Engine(ABC):

    def __init__(self, events) -> None:
        self.events = events

    def run(self):
        pass


class SimulatedAnnealingEngine(Engine):

    def __init__(self, events) -> None:
        super().__init__(events)
        self.schedule = scdule.generate_schedule(self.events)


    def run(self):
        for i in range(1,1000):
            newSchedule = self.step()

            # if not scdule.diff(self.schedule, newSchedule):
            #     print("same!")
            delta = self.calculateDelta(newSchedule)
            # if delta==0:
            #     continue
            if self.simulatedAnnealing(i,10-delta):
                self.schedule=newSchedule
            else:
                print("not_taken")
        return self.schedule

    def calculateDelta(self,newSchedule):

        curr_clashes = self.get_clashes_in_schedule(self.schedule)
        print("curr_clashes="+str(len(curr_clashes)))
        new_clashes = self.get_clashes_in_schedule(newSchedule)
        print("new_clashes="+str(len(new_clashes)))

        return len(curr_clashes)-len(new_clashes)

    def get_clashes_in_schedule(self, schedule, type=None):
        clashes = []

        schedule.instances.sort(key=lambda x: x.start_time, reverse=False)
        for i in range(0, len(schedule.instances) - 1):
            k = 1
            while (i+k) < len(schedule.instances) and schedule.instances[i].end_time > schedule.instances[i + k].start_time:
                if type == "operative" and schedule.instances[i].description.split("-")[0]=="Flt":
                    clashes.append(schedule.instances[i])
                else:
                    clashes.append(schedule.instances[i])
                k += 1

        return clashes

    def step (self):

        clashes = self.get_clashes_in_schedule(self.schedule,"operative")

        if len(clashes)==0:
            return self.schedule

        step_clash_instance = random.choice(clashes)

        step_clash_event = self.events[step_clash_instance.event_index]

        new_instance = random.choice(step_clash_event.instances)

        new_schedule = scdule.Schedule(self.schedule.instances.copy())

        new_schedule.instances.remove(step_clash_instance)

        new_schedule.instances.append(new_instance)

        return new_schedule

    def simulatedAnnealing(self, time, delta):
        import random
        random = random.uniform(0,1)
        print("random = " + str(random))
        print("time = " + str(time))
        print("delta = " + str(delta))
        simulated_exp = math.exp(float(delta)/float(time))-1
        print("simulated_exp = " + str(simulated_exp))
        retval = simulated_exp < random
        print("retaval = " + str(retval))
        return retval

    # //calculates SA value
    # public static boolean simulatedAnnealing(double delta, Date time){
    #     float random = new Random().nextFloat();
    #     return (Math.exp(delta/(double) (new Date().getTime()-time.getTime())))<random;
    # }
    # // invoke rule for SA
    # if (simulatedAnnealing(initValue - newValue, time))
    #     return newColorClasses;
    # else return colorClasses;


class GeneticEngine(Engine):

    schedules = []

    def __init__(self, events, population_size, elitism_factor, mutation_rate ,generations) -> None:
        super().__init__(events)
        self.mutation_rate = mutation_rate
        self.population_size = population_size
        self.population_size = population_size
        self.elitism_factor = elitism_factor
        self.generations = generations


    def run(self):
        population = pop.Population(self.events).generate(self.population_size)
        population.calculate_fitness()
        generations = self.generations
        while population.best_fitness() > 0 and generations > 0:

            population.calculate_fitness()
            population.sort()

            print("Generation = " + str(self.generations - generations) +
                  ", Best fitness = " + str(population.best_fitness())+
                  ", Worst fitness = " + str(population.genes[self.population_size-1].fitness))

            elite_population, common_population = population.elitism(self.elitism_factor)
            common_population.mate(elite_population)
            common_population.mutation(self.mutation_rate)
            population = pop.Population.combine(elite_population,common_population)
            generations-=1

        print("====================================================")
        print("Generation = " + str(self.generations - generations) +
              ", Best fitness = " + str(population.best_fitness()) +
              ", Worst fitness = " + str(population.genes[self.population_size - 1].fitness))

        return population.genes[0].schedule

