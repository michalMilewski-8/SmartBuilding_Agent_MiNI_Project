import datetime

class Calendar:
    def __init__(self, room_idle_temp = 16):
        self.events = {}
        self.room_idle_temp = room_idle_temp;

    def add_event(self, guid, start_date, end_date, temp=22):
        self.events[guid] = (start_date, end_date, temp)

    def delete_event(self, guid):
        self.events.pop(guid, None)

    def modify_event(self, guid, start_date, end_date, temp=22):
        self.add_event(guid, start_date, end_date, temp)

    def get_events(self):
        return self.events

    def get_event(self, guid):
        if guid in self.events.keys():
            return self.events[guid]

    def is_free(self, start_date, end_date):
        for start, end, temp in self.events.values():
            if start <= start_date < end:
                return False
            if start < end_date <= end:
                return False
        return True

    def closest_meeting_by_start_to_end(self,start_date):
        def compare(x, st):
            if st >= x:
                return st-x
            else:
                return None
        return min(self.events, key= lambda x: compare(x[1][1], start_date))

    def closest_meeting_by_end_to_start(self, end_date):
        def compare(x, st):
            if st <= x:
                return x - st
            else:
                return None
        return min(self.events, key=lambda x: compare(x[1][0], end_date))

    def calculate_points(self, start_date, end_date, temp):
        if self.is_free(start_date, end_date):
            closest_before = self.closest_meeting_by_start_to_end(start_date)
            closest_after = self.closest_meeting_by_end_to_start(end_date)
            result = 0
            if closest_after is not None:
                dist_to = end_date - closest_after[1][0]
                result += abs(temp - closest_after[1][2]) * dist_to
            else:
                result += abs(self.room_idle_temp - temp) * 1000

            if closest_before is not None:
                dist_bef = end_date - closest_before[1][0]
                result += abs(temp - closest_before[1][2]) * dist_bef
            else:
                result += abs(self.room_idle_temp - temp) * 1000
        else:
            return float('inf')

    def calculate_points_as_neighbour(self, start_date, end_date, temp):
        if self.is_free(start_date, end_date):
            return abs(self.room_idle_temp - temp) * (end_date - start_date)
        else:
            result = 0
            look_date_start = start_date
            look_date_end = end_date
            for start, end, temp_ in self.events:
                if start < look_date_end and end > look_date_start:
                    if start > look_date_start and end < look_date_end:
                        result += abs(temp_ - temp) * (end - start)
                        result += self.calculate_points_as_neighbour(look_date_start, start, temp)
                        result += self.calculate_points_as_neighbour(end, look_date_end, temp)
                    elif start > look_date_start:
                        result += abs(temp_ - temp) * (look_date_end - start)
                        result += self.calculate_points_as_neighbour(look_date_start, start, temp)
                    else:
                        result += abs(temp_ - temp) * (end - look_date_start)
                        result += self.calculate_points_as_neighbour(end, look_date_end, temp)
                    break
            return result

    def delete_old_events(self, date):
        for guid in self.events:
            if self.events[guid][1] < date:
                self.delete_event(guid)

    def get_temperature_at(self, date):
        temp_before = self.room_idle_temp
        temp_after = self.room_idle_temp
        date_before = datetime.datetime(1900,1,1)
        date_after = datetime.datetime(2100,1,1)
        for start, end, temp in self.events.values():
            if end <= date and end > date_before:
                temp_before = temp
            if start >= date and start < date_after:
                temp_after = temp
        return (temp_after+temp_before)/2

    def get_proximity_peek(self, date, time_period):
        preferred_temp = None
        start_time = None
        diff = float('Inf')
        for start, end, temp in self.events.values():
            if start <= date < end:
                preferred_temp = temp
                start_time = datetime.datetime.fromtimestamp(date.timestamp()+time_period)
                return start_time, preferred_temp
            if (date.timestamp()+time_period) >= start.timestamp() > date.timestamp():
                if diff > start.timestamp() - date.timestamp():
                    preferred_temp = temp
                    start_time = start
                    diff = start.timestamp() - date.timestamp()

        return start_time, preferred_temp
