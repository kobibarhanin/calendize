from abc import ABC
from oauth2client import file, client, tools
from httplib2 import Http
from googleapiclient.discovery import build
import datetime
from dateutil.parser import parse as dtparse

import Instance as ins


class Source(ABC):

    def get_instances(self, from_time, to_time):
        raw_instances = self.get_raw_instances(from_time, to_time)
        instances = self.parse_instances(raw_instances)
        return instances, raw_instances

    def get_raw_instances(self, from_time, to_time):
        pass

    def parse_instances(self,raw_events):
        pass

    def upload_instance(self,instance):
        pass

    def clear(self,instances):
        pass



class GoogleO2AuthSource(Source):

    def __init__(self,service) -> None:
        super().__init__()
        self.service = service


    def get_raw_instances(self, from_time, to_time):
        instances_result = self.service.events().list(calendarId='primary', timeMin=from_time,
                                              timeMax=to_time, singleEvents=True,
                                              orderBy='startTime').execute()
        instances = instances_result.get('items', [])
        if not instances:
            print('No upcoming events found.')
        return instances


    def parse_instances(self, raw_instances):
        instances = []
        for raw_instance in raw_instances:
            start_time = self.parse_time(raw_instance, 'start')
            end_time = self.parse_time(raw_instance, 'end')

            if "colorId" in raw_instance.keys():
                colorId=raw_instance["colorId"]
            else:
                colorId="1"
            instances.append(ins.GoogleInstance(raw_instance['summary'], raw_instance['summary'], start_time, end_time, raw_instance["id"],colorId))
        return instances


    def parse_time(self, raw_event, time_type):
        time_raw = raw_event[time_type].get('dateTime', raw_event[time_type].get('date'))
        time_format = datetime.datetime.strftime(dtparse(time_raw), format='%Y,%m,%d,%H,%M')
        year, month, day, hour, minute = time_format.split(",")
        time = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
        return time


    def upload_instance(self, instance):
        self.service.events().insert(calendarId='primary', body=instance).execute()


    def clear(self,instances):
        for instance in instances:
            self.service.events().delete(calendarId='primary', eventId=instance["id"]).execute()



class GoogleCalendarSource(Source):

    def __init__(self,token_path, credentials_path,scope) -> None:
        super().__init__()
        store = file.Storage(token_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(credentials_path, scope)
            credentials = tools.run_flow(flow, store)
        self.service = build('calendar', 'v3', http=credentials.authorize(Http()))


    def get_raw_instances(self, from_time, to_time):
        instances_result = self.service.events().list(calendarId='primary', timeMin=from_time,
                                              timeMax=to_time, singleEvents=True,
                                              orderBy='startTime').execute()
        instances = instances_result.get('items', [])
        if not instances:
            print('No upcoming events found.')
        return instances


    def parse_instances(self, raw_instances):
        instances = []
        for raw_instance in raw_instances:
            start_time = self.parse_time(raw_instance, 'start')
            end_time = self.parse_time(raw_instance, 'end')

            if "colorId" in raw_instance.keys():
                colorId=raw_instance["colorId"]
            else:
                colorId="1"
            instances.append(ins.GoogleInstance(raw_instance['summary'], raw_instance['summary'], start_time, end_time, raw_instance["id"],colorId))
        return instances


    def parse_time(self, raw_event, time_type):
        time_raw = raw_event[time_type].get('dateTime', raw_event[time_type].get('date'))
        time_format = datetime.datetime.strftime(dtparse(time_raw), format='%Y,%m,%d,%H,%M')
        year, month, day, hour, minute = time_format.split(",")
        time = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
        return time


    def upload_instance(self, instance):
        self.service.events().insert(calendarId='primary', body=instance).execute()


    def clear(self,instances):
        for instance in instances:
            self.service.events().delete(calendarId='primary', eventId=instance["id"]).execute()



