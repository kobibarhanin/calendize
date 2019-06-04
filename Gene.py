import random

class Gene:

    # fitness = 0

    def __init__(self, schedule) -> None:
        super().__init__()
        self.schedule = schedule
        self.fitness = 0


    def set_schedule(self,schedule):
        self.schedule = schedule


    def mutate(self, events):

        event = random.choice(events)
        while event.__class__.__name__ != "FloatingEvent" :
            event = random.choice(events)

        mut_instance = random.choice(event.instances)

        self.schedule.instances.append(mut_instance)

        for instance in self.schedule.instances:
            if instance.title == mut_instance.title:
                self.schedule.instances.remove(instance)
                break


    def calculate_fitness(self):
        self.fitness = 0
        self.schedule.instances.sort(key=lambda x: x.start_time, reverse=False)
        for i in range(0, len(self.schedule.instances) - 1):
            k = 1
            while (i+k) < len(self.schedule.instances) and self.schedule.instances[i].end_time > self.schedule.instances[i + k].start_time:
                self.fitness += 1
                k += 1
