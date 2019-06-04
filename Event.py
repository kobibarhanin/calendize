from abc import ABC
import Instance as ins

class Event(ABC):

    def __init__(self, title, description, instances,colorId = None) -> None:
        self.title = title
        self.description = description
        self.instances = instances
        self.colorId = colorId

    def __set__(self, instance, value):
        pass


class AnchorEvent(Event):



    def __init__(self, title, description, instances, colorId=None) -> None:
        super().__init__(title, description, instances, colorId)

    def __set__(self, instance, chosen_instance):
        self.chosen_instance = chosen_instance


class FloatingEvent(Event):


    def __init__(self, title, description, instances, colorId=None) -> None:
        super().__init__(title, description, instances, colorId)

    def add_new_instance(self,start_time, end_time,event_index,instance_id):
        instance = ins.GoogleInstance(self.title,self.description,start_time,end_time,instance_id,self.colorId)
        instance.event_index=event_index
        self.instances.append(instance)

    def __set__(self, instance, value):
        super().__set__(instance, value)