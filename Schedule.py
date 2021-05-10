import json
import random
from Event import AnchorEvent

class Schedule:

    def __init__(self, instances = None) -> None:
        if instances is None:
            self.instances = []
        else:
            self.instances = instances


    def add_instance(self, instance):
        self.instances.append(instance)


    def print(self):
        for instance in self.instances:
            instance.print()


    def upload(self, source):
        for instance in self.instances:
            instance.upload(source)


    def write_to_file(self, path):
        data = []
        for instance in self.instances:
            instance_data = instance.get_json()
            data.append(instance_data)
        with open(path, 'w') as outfile:
            json.dump(data, outfile)


    def to_json(self):
        data = []
        for instance in self.instances:
            instance_data = instance.to_json()
            data.append(instance_data)
        return data


def generate_schedule(events):
    schedule = Schedule()
    for event in events:
        if event.instances is AnchorEvent:
            schedule.add_instance(event.instances[0])
        else:
            schedule.add_instance(random.choice(event.instances))
    return schedule


def diff(sched1, sched2):
    for i in range (len(sched1.instances)):
        if sched1.instances[i]!=sched2.instances[i]:
            return True
    return False