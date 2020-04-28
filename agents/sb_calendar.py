import datetime

class Calendar:
    def __init__(self):
        self.events = {}

    def add_event(self, guid, start_date, end_date):
        self.events[guid] = (start_date, end_date)

    def delete_event(self, guid):
        self.events.pop(guid, None)

    def modify_event(self, guid, start_date, end_date):
        self.add_event(guid, start_date, end_date)

    def get_events(self):
        return self.events

    def get_event(self, guid):
        if guid in self.events.keys():
            return self.events[guid]

    def is_free(self, start_date, end_date):
        for start, end in self.events.values():
            if start <= start_date < end:
                return False
            if start < end_date <= end:
                return False
        return True

    def delete_old_events(self, date):
        for guid in self.events:
            if self.events[guid] < date:
                self.delete_event(guid)
