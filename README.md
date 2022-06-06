# [Calendize](https://calendize.herokuapp.com/calculator) - weekly schedule optimization platform

![alt text](https://github.com/kobibarhanin/calendize/blob/master/static/calendize_landing.png?raw=true)

Calendize was my BSC project at University of Haifa CS.

The idea is to utilize optimization algorithms such as [Genetic Algorithms](https://en.wikipedia.org/wiki/Genetic_algorithm) to solve the [Constraints Satisfaction Problems (CSPs)](https://en.wikipedia.org/wiki/Constraint_satisfaction_problem) that is ordering a complex weekly schedule.

## The process

- Visit Calendize at: <https://calendize.herokuapp.com>
- You will be requested to authenticate with your google account so we can fetch the events you wish to calculate the optimal scheduling for.
- Set a time interval for fetching events. Your events will be brought to the platform.
- Classify your events by [categories](https://github.com/kobibarhanin/calendize/blob/master/static/events_classes.png?raw=true):
  - Anchor Events: Must happen at the time stated.
  - Floating Events: Should happen once, time can change based on optional slots given (must be the same name).
  - Opportune Events: Could happen, if the requested time slot is available.
  - Routine Events: Could happen, if any of the time range allows it.
- Look [here](https://github.com/kobibarhanin/calendize/blob/master/static/from_cal.png?raw=true) to get a better understanding of how events are expected to be classified (Anc, Flt). See result [here](https://github.com/kobibarhanin/calendize/blob/master/static/to_cal.png?raw=true).
- Select the algorithm and parameters (leave default parameters if you have no knowledge of the algorithm).
- Calendize.

**Notice: at the moment the system can only address interchangeable events if they have the same name. (applies for floating events)**