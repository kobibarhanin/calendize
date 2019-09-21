from abc import ABC
import math
import random

import Event
import Schedule as scdule
import Population as pop


class Engine(ABC):
    iteration_value = []
    adapted_timestamps = []
    purge_timestamps = []

    def __init__(self, events) -> None:
        self.events = events

    def run(self):
        self.iteration_value = []
        self.adapted_timestamps = []
        self.purge_timestamps = []


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
            self.adapted_timestamps.append(time)
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
            if len(self.curr_clashes) == 0:
                self.best_result = 0
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
            self.best_result = len(tmp_schedule_res)
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
        return_value = simulated_exp > rand_coefficient
        print(f'simulating: time = {time}, delta = {delta}, exponent = {simulated_exp}'
              f' - taken? {return_value}')
        return return_value


class GeneticEngine(Engine):

    schedules = []

    def __init__(self, events, population_size, elitism_factor, mutation_rate, generations,
                 adaptive=False, enable_purge=False, adaptive_lookback=5, purge_lookback=10, purge_effect=1,
                 selection_type=0) -> None:
        super().__init__(events)
        self.mutation_rate = mutation_rate
        self.population_size = population_size
        self.elitism_factor = elitism_factor
        self.generations = generations
        self.elitism_factor_base = elitism_factor
        self.mutation_rate_base = mutation_rate
        self.purge_iteration = 0
        self.adaptive = adaptive
        self.enable_purge = enable_purge
        self.adaptive_lookback = adaptive_lookback
        self.purge_lookback = purge_lookback
        self.purge_effect = purge_effect
        self.selection_type = selection_type

        self.best_result = 100
        self.best_schedule = None

    def adapt_mutation_factor(self, time):

        if time < self.adaptive_lookback:
            return

        rand_coefficient = random.uniform(0, 1)
        simulated_exp = math.exp(1 / float(math.sqrt(time - self.purge_iteration))) - 1
        if not simulated_exp < rand_coefficient:
            lookback = self.adaptive_lookback
            adapt_mutate = True
            lookback_table = []
            for i in range(len(self.iteration_value)-lookback, len(self.iteration_value)):
                lookback_table.append(self.iteration_value[i])
                if self.iteration_value[i] != self.iteration_value[len(self.iteration_value)-1]:
                    adapt_mutate = False
            print(f'> simulated annealing = {simulated_exp} => lookback_table = {str(lookback_table)}, taken? {adapt_mutate}')
            if adapt_mutate and self.mutation_rate < 0.5:
                self.adapted_timestamps.append(time)
                self.mutation_rate += 0.05
                print(f'>> Mutation factor adapted to: {self.mutation_rate}')

    def check_purge(self, time, population):
        lookback = self.purge_lookback
        if time < lookback:
            return
        purge = True
        lookback_table = []
        for i in range(len(self.iteration_value)-lookback, len(self.iteration_value)):
            lookback_table.append(self.iteration_value[i])
            if self.iteration_value[i] != self.iteration_value[len(self.iteration_value)-1]:
                purge = False

        if purge and time > lookback + self.purge_iteration:
            print(f'>> Purging: {self.purge_effect * 100} percent of the population')
            self.purge_timestamps.append(time)
            self.purge_iteration = time
            kill_num = int(self.population_size * self.purge_effect)
            population.purge(kill_num)
            population.calculate_fitness()
            population.sort()
            self.mutation_rate = self.mutation_rate_base

    def run(self):
        super().run()
        population = pop.Population(self.events).generate(self.population_size)
        population.calculate_fitness()
        population.sort()
        generations = self.generations
        generation = 0
        best_fitness = 1

        while best_fitness > 0 and generations > 0:

            elite_population, common_population = population.elitism(self.elitism_factor)
            common_population.mate(elite_population, self.selection_type)
            common_population.mutation(self.mutation_rate)
            population = pop.Population.combine(elite_population, common_population)

            population.calculate_fitness()
            population.sort()

            best_fitness = population.best_fitness()
            if best_fitness < self.best_result:
                self.best_result = best_fitness
                self.best_schedule = population.genes[0].schedule

            self.iteration_value.append(best_fitness)
            print(f'Generation = {generation}, best_fitness = {best_fitness}, '
                  f'worst_fitness = {population.genes[self.population_size-1].fitness}')

            if self.adaptive:
                self.adapt_mutation_factor(generation)
            if self.enable_purge:
                self.check_purge(generation, population)

            generations -= 1
            generation += 1

        print(f'====================================================\n'
              f'*** Generation = {generation}, best_fitness = {best_fitness}, '
              f'worst_fitness = {population.genes[self.population_size - 1].fitness} ***')

        return self.best_schedule, self.best_result

