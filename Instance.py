from abc import ABC


class Instance(ABC):

    def __init__(self, title, description, start_time, end_time, instance_id = None, colorId = None) -> None:
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.instance_id = instance_id
        self.colorId = colorId

    def print(self):
        print("==============\n"
              "Title: " + self.title +"\n"+
              "Description: " + self.description+ "\n"+
              "Start Time: " + str(self.start_time)+ "\n" +
              "End Time: " + str(self.end_time)+ "\n")

    def upload(self, source):
        pass

    def to_json(self):
        pass

    def add_event_index(self, index):
        self.event_index = index


class GoogleInstance(Instance):

    def __init__(self, title, description, start_time, end_time, instance_id=None, colorId=None) -> None:
        super().__init__(title, description, start_time, end_time, instance_id, colorId)

    def upload(self, source):
        instance = {
            'summary': self.title,
            'description': self.description,
            'colorId': self.colorId,
            'start': {
                'dateTime': GoogleInstance.parse_time_object(self.start_time),
                'timeZone': 'Asia/Jerusalem',
            },
            'end': {
                'dateTime': GoogleInstance.parse_time_object(self.end_time),
                'timeZone': 'Asia/Jerusalem',
            },
        }
        source.upload_instance(instance)

    @classmethod
    def parse_time_object(cls, time):
        date, hour = str(time).split()
        parsed_time = date + "T" + hour
        return parsed_time

    @classmethod
    def color_transfer(cls, colorId):
        return cls.google_colors[str(colorId)]


    def to_json(self):
        return {'title': self.title,
                'start': GoogleInstance.parse_time_object(self.start_time),
                'end': GoogleInstance.parse_time_object(self.end_time),
                'color':GoogleInstance.color_transfer(self.colorId),
                'id':self.instance_id
                }


    google_colors = {
        "1":"#a4bdfc",
        "2":"#7ae7bf",
        "3":"#dbadff",
        "4":"#ff887c",
        "5":"#fbd75b",
        "6":"#ffb878",
        "7":"#46d6db",
        "8":"#e1e1e1",
        "9":"#5484ed",
        "10":"#51b749",
        "11":"#dc2127",
    }