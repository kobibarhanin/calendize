from __future__ import print_function

import Source as src
import Event as evnt
import Engine as eng
import Instance as inst


def fetch(start_date='2018-12-23T08:00:00Z', end_date='2018-12-29T22:00:00Z', service=None):
    google_source = src.GoogleO2AuthSource(service)
    instances, _ = google_source.get_instances(start_date, end_date)
    return [instance.to_json() for instance in instances]


def run(start_date='2018-12-23T08:00:00Z', end_date='2018-12-29T22:00:00Z', anchor_instances=None,
        floating_instances=None, routine_instances=None, algorithm='Genetic Algorithm', service=None, options=None):
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
            print("UNALLOCATED INSTANCE: " + instance.title + " , " + instance.instance_id)

    if routine_instances:
        for instance in routine_instances:
            name, duration, start_time, end_time = instance.split(";")
            duration_parts = duration.split(":")
            hours = int(duration_parts[0])
            minutes = 0
            if len(duration_parts) > 1:
                minutes = int(duration_parts[1])
            rand_routine_instances = [inst.RandomInstance(name, hours, minutes, int(start_time), int(end_time)),
                                      inst.RandomInstance(name, hours, minutes, int(start_time), int(end_time)),
                                      inst.RandomInstance(name, hours, minutes, int(start_time), int(end_time))]
            events.append(evnt.FloatingEvent(name, name, rand_routine_instances, '#a4bdfc'))


    # === Section 3 (Calculate): Use some engine to build an optimal schedule === #
    if algorithm == 'Genetic Algorithm':

        run_args = {
            "population_size": 40,
            "elitism_factor": 0.1,
            "mutation_rate": 0.3,
            "generations": 30,
            "selection_type": 0,
            "adaptive": True,
            "adaptive_lookback": 5,
            "enable_purge": True,
            "purge_lookback": 10,
            "purge_effect": 1,
        }

        if options:
            run_args = options

        engine = eng.GeneticEngine(events,
                                   population_size=run_args["population_size"],
                                   elitism_factor=run_args["elitism_factor"],
                                   mutation_rate=run_args["mutation_rate"],
                                   generations=run_args["generations"],
                                   selection_type=run_args["selection_type"],
                                   adaptive=run_args["adaptive"],
                                   adaptive_lookback=run_args["adaptive_lookback"],
                                   enable_purge=run_args["enable_purge"],
                                   purge_lookback=run_args["purge_lookback"],
                                   purge_effect=run_args["purge_effect"],
                                   )
        data, best = engine.run()
        result = True if best == 0 else False
    elif algorithm == 'Simulated Annealing':

        run_args = {
            "iterations": 100,
            "adaptive": True,
            "adaptive_lookback": 5,
        }

        if options:
            run_args = options

        engine = eng.SimulatedAnnealingEngine(events,
                                              iterations=run_args["iterations"],
                                              adaptive=run_args["adaptive"],
                                              adaptive_lookback=run_args["adaptive_lookback"]
                                              )
        data, best = engine.run()
        result = engine.best_result
    else:
        raise Exception(f'undefined algorithm: {algorithm}')

    print(f'*** Result layout: {engine.iteration_value} ***')

    jsoned_data = data.to_json()
    jsoned_data.append(engine.iteration_value)
    jsoned_data.append(engine.adapted_timestamps)
    jsoned_data.append(engine.purge_timestamps)
    jsoned_data.append(engine.best_result)
    return jsoned_data, result

    # === Section 4 (Upload): Upload schedule to source (GUI, Calendar) === #

    # google_source.clear(raw_instances)
    # schedule.upload(google_source)


if __name__ == '__main__':
    run()