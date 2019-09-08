from __future__ import print_function

import Source as src
import Event as evnt
import Engine as eng


def fetch(start_date='2018-12-23T08:00:00Z', end_date='2018-12-29T22:00:00Z', service=None):
    google_source = src.GoogleO2AuthSource(service)
    instances, _ = google_source.get_instances(start_date, end_date)
    return [instance.to_json() for instance in instances]


def run(start_date='2018-12-23T08:00:00Z', end_date='2018-12-29T22:00:00Z', anchor_instances=None,
        floating_instances=None, algorithm = 'Genetic Algorithm',service=None):
    # === Section 1 (Source): Read data from source === #
    google_source = src.GoogleO2AuthSource(service)
    instances, raw_instances = google_source.get_instances(start_date, end_date)

    # === Section 2 (User): Tag and cluster data with event type: anchor, float. for testing === #
    events = []
    floating_events = dict()
    for instance in instances:
        if instance.instance_id in anchor_instances:
            instance.add_event_index(len(events))
            events.append(evnt.AnchorEvent(instance.title,instance.description,[instance],instance.colorId))
        elif instance.instance_id in floating_instances:
            if instance.title in floating_events:
                instance.add_event_index(floating_events[instance.title].instances[0].event_index)
                floating_events[instance.title].add_new_instance(instance.start_time, instance.end_time,
                                                                 instance.event_index, instance.instance_id)
            else:
                instance.add_event_index(len(events))
                floating_events[instance.title] = evnt.FloatingEvent(instance.title, instance.description, [instance],
                                                                   instance.colorId)
                events.append(floating_events[instance.title])
        else:
            print("UNALLOCATED INSTANCE: " + instance.title + " , "+ instance.instance_id)


    # events = []
    # floating_events = dict()
    # for instance in instances:
    #     pref = instance.title.split("-")[0]
    #     if pref == "Anc":
    #         instance.add_event_index(len(events))
    #         events.append(evnt.AnchorEvent(instance.title,instance.description,[instance],instance.colorId))
    #     elif pref == "Flt":
    #         if instance.title in floating_events:
    #             instance.add_event_index(floating_events[instance.title].instances[0].event_index)
    #             floating_events[instance.title].add_new_instance(instance.start_time,instance.end_time,instance.event_index,instance.instance_id)
    #         else:
    #             instance.add_event_index(len(events))
    #             floating_events[instance.title]=evnt.FloatingEvent(instance.title,instance.description,[instance],instance.colorId)
    #             events.append(floating_events[instance.title])

    # === Section 3 (Calculate): Use some engine to build an optimal schedule === #
    if algorithm == 'Genetic Algorithm':
        engine = eng.GeneticEngine(events, population_size=100, elitism_factor=0.2, mutation_rate=0.2, generations=20)
        data, best = engine.run()
        result = True if best == 0 else False
    elif algorithm == 'Simulated Annealing':
        engine = eng.SimulatedAnnealingEngine(events)
        data = engine.run()
        result = None
    else:
        raise Exception(f'undefined algorithm: {algorithm}')

    return data.to_json(), result

    # === Section 4 (Upload): Upload schedule to source (GUI, Calendar) === #

    # google_source.clear(raw_instances)
    # schedule.upload(google_source)


if __name__ == '__main__':
    run()