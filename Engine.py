from abc import ABC

import math
import random

import Event
import Schedule as scdule
import Population as pop


class Engine(ABC):

    iteration_value = []

    def __init__(self, events) -> None:
        self.events = events


    def run(self):
        self.iteration_value = []


class SimulatedAnnealingEngine(Engine):

    def __init__(self, events, iterations, adaptive, adaptive_lookback) -> None:
        super().__init__(events)
        self.iterations = iterations
        self.schedule = scdule.generate_schedule(self.events)
        self.adaptive = adaptive
        self.adaptive_lookback = adaptive_lookback
        self.best_result = len(self.get_clashes_in_schedule(self.schedule))
        self.best_schedule = self.schedule

    def adapt_simulator(self, time):

        if time < self.adaptive_lookback:
            return

        rand_coefficient = random.uniform(0, 1)
        simulated_exp = math.exp(1/float(math.log(time)))-1
        if not simulated_exp < rand_coefficient:
            return

        lookback = self.adaptive_lookback
        adapt_sa = True
        lookback_table = []
        for i in range(len(self.iteration_value)-lookback, len(self.iteration_value)):
            lookback_table.append(self.iteration_value[i])
            if self.iteration_value[i] != self.iteration_value[len(self.iteration_value)-1]:
                adapt_sa = False

        print(f'lookback_table = {str(lookback_table)}, taken? {adapt_sa}')

        if adapt_sa:
            tmp_schedule_res = self.get_clashes_in_schedule(self.schedule)
            if len(tmp_schedule_res) < self.best_result:
                self.best_schedule = self.schedule
                self.best_result = len(tmp_schedule_res)
            self.schedule = scdule.generate_schedule(self.events)


    def run(self):
        super().run()
        for i in range(1, self.iterations):
            new_schedule = self.step(i)
            delta = self.calculate_delta(new_schedule)
            if self.curr_clashes == 0:
                return self.schedule, True
            if delta > 0 or self.simulated_annealing(i, abs(delta)):
                print(f'taking new schedule with delta {delta}')
                self.schedule = new_schedule
                self.iteration_value.append(len(self.new_clashes))
            else:
                self.iteration_value.append(len(self.curr_clashes))
                if self.adaptive:
                    self.adapt_simulator(i)
        tmp_schedule_res = self.get_clashes_in_schedule(self.schedule)
        if len(tmp_schedule_res) < self.best_result:
            return self.schedule, True
        return self.best_schedule, True

    def calculate_delta(self, new_schedule):
        self.curr_clashes = self.get_clashes_in_schedule(self.schedule)
        self.new_clashes = self.get_clashes_in_schedule(new_schedule)
        print(f'curr_clashes: {len(self.curr_clashes)}, new_clashes: {len(self.new_clashes)}')
        return len(self.curr_clashes)-len(self.new_clashes)

    def get_clashes_in_schedule(self, schedule, type=None):
        clashes = []
        schedule.instances.sort(key=lambda x: x.start_time, reverse=False)
        for i in range(0, len(schedule.instances) - 1):
            k = 1
            while (i+k) < len(schedule.instances) and schedule.instances[i].end_time > schedule.instances[i + k].start_time:
                if type == "operative" and isinstance(self.events[schedule.instances[i].event_index], Event.FloatingEvent):
                    clashes.append(schedule.instances[i])
                else:
                    clashes.append(schedule.instances[i])
                k += 1

        return clashes

    def step(self, iteration):
        clashes = self.get_clashes_in_schedule(self.schedule, "operative")
        if iteration == 1:
            self.max_clash = len(clashes)
        if len(clashes) == 0:
            return self.schedule
        step_clash_instance = random.choice(clashes)
        step_clash_event = self.events[step_clash_instance.event_index]
        new_instance = random.choice(step_clash_event.instances)
        new_schedule = scdule.Schedule(self.schedule.instances.copy())
        new_schedule.instances.remove(step_clash_instance)
        new_schedule.instances.append(new_instance)
        return new_schedule

    def simulated_annealing(self, time, delta):
        rand_coefficient = random.uniform(0, 1)
        simulated_exp = math.exp((self.max_clash - float(delta))/float(time))-1
        # simulated_exp = math.exp(1/float(time))-1
        print(f'simulating: time = {time}, delta = {delta}, exponent = {simulated_exp} - taken? {simulated_exp < rand_coefficient}')
        return simulated_exp < rand_coefficient


class GeneticEngine(Engine):

    schedules = []

    def __init__(self, events, population_size, elitism_factor, mutation_rate, generations,
                 adaptive=False, enable_plague=False, adaptive_lookback=5, plague_lookback=10, plague_effect=1) -> None:
        super().__init__(events)
        self.mutation_rate = mutation_rate
        self.population_size = population_size
        self.elitism_factor = elitism_factor
        self.generations = generations
        self.elitism_factor_base = elitism_factor
        self.mutation_rate_base = mutation_rate
        self.plague_iteration = 0
        self.adaptive = adaptive
        self.enable_plague = enable_plague
        self.adaptive_lookback = adaptive_lookback
        self.plague_lookback = plague_lookback
        self.plague_effect = plague_effect

    def adapt_mutation_factor(self, time):

        if time < self.adaptive_lookback:
            return

        rand_coefficient = random.uniform(0, 1)
        simulated_exp = math.exp(1/float(math.sqrt(time-self.plague_iteration)))-1
        if not simulated_exp < rand_coefficient:
            lookback = self.adaptive_lookback
            adapt_mutate = True
            lookback_table = []
            for i in range(len(self.iteration_value)-lookback, len(self.iteration_value)):
                lookback_table.append(self.iteration_value[i])
                if self.iteration_value[i] != self.iteration_value[len(self.iteration_value)-1]:
                    adapt_mutate = False
            print(f'simulated_exp = {simulated_exp} => lookback_table = {str(lookback_table)}, taken? {adapt_mutate}')
            if adapt_mutate and self.mutation_rate < 0.5:
                self.mutation_rate += 0.05
                print(f'mutation factor adapted to: {self.mutation_rate}')

    def check_plague(self, time, population):
        lookback = self.plague_lookback
        if time < lookback:
            return
        plague = True
        lookback_table = []
        for i in range(len(self.iteration_value)-lookback, len(self.iteration_value)):
            lookback_table.append(self.iteration_value[i])
            if self.iteration_value[i] != self.iteration_value[len(self.iteration_value)-1]:
                plague = False

        if plague and time > lookback + self.plague_iteration:
            self.plague_iteration = time
            print(f'killine {self.plague_effect} of population')
            kill_num = int(self.population_size * self.plague_effect)
            population.plague(kill_num)
            population.calculate_fitness()
            population.sort()
            self.mutation_rate = self.mutation_rate_base

    def run(self):
        super().run()
        population = pop.Population(self.events).generate(self.population_size)
        population.calculate_fitness()
        generations = self.generations
        while population.best_fitness() > 0 and generations > 0:

            generation = self.generations - generations

            elite_population, common_population = population.elitism(self.elitism_factor)
            common_population.mate(elite_population)
            common_population.mutation(self.mutation_rate)
            population = pop.Population.combine(elite_population, common_population)
            generations -= 1

            population.calculate_fitness()
            population.sort()

            best_fitness = population.best_fitness()

            self.iteration_value.append(best_fitness)
            print(f'Generation = {generation}, best_fitness = {best_fitness}, '
                  f'worst_fitness = {population.genes[self.population_size-1].fitness}')

            if self.adaptive:
                self.adapt_mutation_factor(generation)
            if self.enable_plague:
                self.check_plague(generation, population)


        print("====================================================")
        print("FINAL - Generation = " + str(self.generations - generations) +
              ", Best fitness = " + str(population.best_fitness()) +
              ", Worst fitness = " + str(population.genes[self.population_size - 1].fitness))
        self.best_result = str(population.best_fitness())
        return population.genes[0].schedule, population.best_fitness()

