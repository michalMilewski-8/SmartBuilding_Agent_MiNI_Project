from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
from ..sb_calendar import Calendar
import json
from datetime import datetime
from ..time_conversion import time_to_str, str_to_time


class CentralAgent(Agent):
    date = None
    meeting_room_calendars = {}
    # meeting_room_neighbours = {}
    meetings_info = {}  # example {"date_start": start_date, "date_end": end_date,
    processing_meeting = False

    #           "temperature": temp, "scores": {room_jid:score}}
    def __init__(self, jid, password):
        super().__init__(jid, password)
        date = None
        meeting_room_calendars = {}
        # meeting_room_neighbours = {}
        meetings_info = {}

    @staticmethod
    def prepare_meeting_score_request(self, receivers, guid, start, end, temperature):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'meeting_score_request')
        msg.body = json.dumps({'meeting-guid': guid, 'start_date': start, 'end_date': end, 'temperature': temperature})
        return msg

    def add_meeting_room(self, room_jid):
        self.meeting_room_calendars[room_jid] = Calendar()

    async def setup(self):
        print(str(self.jid) + " Central agent setup")
        self.date = datetime.now()

        datetime_inform_template = Template()
        datetime_inform_template.set_metadata('performative', 'inform')
        datetime_inform_template.set_metadata("type", "datetime_inform")
        datetime_behaviour = self.ReceiveDatetimeInformBehaviour()
        self.add_behaviour(datetime_behaviour, datetime_inform_template)

        meeting_request_template = Template()
        meeting_request_template.set_metadata('type', 'meet_request')
        meeting_request_template.set_metadata('performative', 'request')
        booking_behaviour = self.MeetingBookingBehaviour()
        self.add_behaviour(booking_behaviour, meeting_request_template)

        meeting_score_template = Template()
        meeting_score_template.set_metadata('type', 'meeting_score_inform')
        meeting_score_template.set_metadata('performative', 'inform')
        self.add_behaviour(self.ReceiveScoreBehaviour(), meeting_score_template)

        meeting_late_template = Template()
        meeting_late_template.set_metadata('performative', 'inform')
        meeting_late_template.set_metadata('type', 'late')
        meeting_late_behaviour = self.MeetingLateBehaviour()
        self.add_behaviour(meeting_late_behaviour, meeting_late_template)

    async def find_best_room(self, behav, meet_guid, start_date, end_date, temp):
        print("find_best_room started")
        for meeting_room in behav.agent.meeting_room_calendars.keys():
            score_request = Message(to=meeting_room)
            score_request.set_metadata("performative", "request")
            score_request.set_metadata("type", "meeting_score_request")
            score_request.body = json.dumps({"meeting_guid": meet_guid,
                                             "start_date": time_to_str(start_date),
                                             "end_date": time_to_str(end_date),
                                             "temperature": temp
                                             })
            await behav.send(score_request)

    # def calculate_points(self, start_date, end_date, temp, room):
    #     result = 0
    #     result += self.meeting_room_calendars[room].calculate_points(start_date, end_date, temp)
    #     for neigh in self.meeting_room_neighbours[room]:
    #         result += self.meeting_room_calendars[neigh].calculate_points_as_neighbour(start_date, end_date, temp)
    #     return result

    async def negotiate(self, behav, msg_guid, best_start_date, best_end_date,
                        receiver):
        move_meeting_propose = Message(to=receiver)
        move_meeting_propose.set_metadata('performative', 'propose')
        move_meeting_propose.set_metadata('type', 'move_meeting_propose')
        move_meeting_propose.body = json.dumps({'meeting_guid': msg_guid, 'start_date': time_to_str(best_start_date),
                                                'end_date': time_to_str(best_end_date)})
        await behav.send(move_meeting_propose)

    async def negotiate_end(self, behav, msg_guid, start_date, end_date,
                            receiver, delete_meeting):
        move_meeting_inform = Message(to=receiver)
        move_meeting_inform.set_metadata('performative', 'inform')
        move_meeting_inform.set_metadata('type', 'move_meeting_inform')
        move_meeting_inform.body = json.dumps({'meeting_guid': msg_guid, 'start_date': time_to_str(start_date),
                                               'end_date': time_to_str(end_date), "delete_meeting": delete_meeting})
        await behav.send(move_meeting_inform)

    async def late_confirm(self, behav, confirmed, receiver):
        late_confirm = Message(to=receiver)
        late_confirm.set_metadata('performative', 'inform')
        late_confirm.set_metadata('type', 'move_meeting_inform')
        late_confirm.body = json.dumps({"confirmed": confirmed})
        await behav.send(late_confirm)

    class ReceiveDatetimeInformBehaviour(CyclicBehaviour):

        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                self.agent.date = str_to_time(msg_data["datetime"])
                print(str(self.agent.jid) + " current date: {}".format(self.agent.date))

    class MeetingBookingBehaviour(CyclicBehaviour):
        async def run(self):
            if not self.agent.processing_meeting:
                msg = await self.receive(timeout=1)
                if msg:
                    print(msg)
                    msg_body = json.loads(msg.body)
                    self.agent.processing_meeting = True
                    self.agent.meetings_info[msg_body.get('meeting_guid')] = {'meeting_guid': msg_body.get('meeting_guid'),
                                                                              'organizer_jid': str(msg.sender),
                                                                              'start_date': str_to_time(
                                                                                  msg_body.get('start_date')),
                                                                              'end_date': str_to_time(
                                                                                  msg_body.get('end_date')),
                                                                              'room_id': None,
                                                                              'temperature': msg_body.get('temperature'),
                                                                              "participants": msg_body.get('participants'),
                                                                              "scores": {}}

                    await self.agent.find_best_room(self, msg_body.get('meeting_guid'),
                                                    str_to_time(msg_body.get('start_date')),
                                                    str_to_time(msg_body.get('end_date')), msg_body.get('temperature'))

    class MeetingLateBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                print(msg)
                msg_body = json.loads(msg.body)
                new_start_date = str_to_time(msg_body['arrival_datetime'])
                guid = msg_body['meeting_guid']
                if msg_body['force_move'] == True:
                    print("DEBUG")
                    old_start_date = self.agent.meetings_info[guid]['start_date']
                    old_end_date = self.agent.meetings_info[guid]['end_date']
                    new_end_date = old_end_date + (new_start_date - old_start_date)
                    self.agent.meetings_info[msg_body["meeting_guid"]]["scores"] = {}
                    self.agent.meetings_info[msg_body["meeting_guid"]]["start_date"] = new_start_date
                    self.agent.meetings_info[msg_body["meeting_guid"]]["end_date"] = new_end_date
                    await self.agent.find_best_room(self, guid, new_start_date, new_end_date,
                                                    self.agent.meetings_info[guid]['temperature'])
                else:
                    self.agent.meetings_info[guid]['start_date'] = new_start_date
                    behav = self.agent.RespondForMeetingRequest()
                    behav.meeting_guid = guid
                    self.agent.add_behaviour(behav)


    class ReceiveScoreBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                # print(msg)
                msg_body = json.loads(msg.body)
                print('received score: ' + str(msg_body["score"]) + ' from: ' + str(msg.sender))
                self.agent.meetings_info[msg_body["meeting_guid"]]["scores"][str(msg.sender)] = msg_body["score"]
                if len(self.agent.meetings_info[msg_body["meeting_guid"]][
                           "scores"]) == len(self.agent.meeting_room_calendars.keys()):
                    behav = self.agent.RespondForMeetingRequest()
                    behav.meeting_guid = msg_body["meeting_guid"]
                    self.agent.add_behaviour(behav)

    class RespondForMeetingRequest(OneShotBehaviour):
        meeting_guid = ""

        async def run(self):

            def check(x):
                if x[1] is None:
                    return float('Inf')
                else:
                    return x[1]

            room_date = min(self.agent.meetings_info[self.meeting_guid]["scores"].items(), key=check)

            self.agent.meetings_info[self.meeting_guid]["room_id"] = room_date[0]

            meeting = self.agent.meetings_info[self.meeting_guid]

            for receiver in meeting.get('participants'):
                response = Message()
                response.set_metadata('performative', 'inform')
                response.set_metadata('type', 'new_meeting_inform')
                response.body = json.dumps({'meeting_guid': self.meeting_guid,
                                            'organizer_jid': meeting["organizer_jid"],
                                            'start_date': time_to_str(meeting['start_date']),
                                            'end_date': time_to_str(meeting['end_date']),
                                            'room_id': meeting['room_id'],
                                            'temperature': meeting['temperature']
                                            })
                response.to = receiver
                await self.send(response)

            response = Message()
            response.set_metadata('performative', 'inform')
            response.set_metadata('type', 'new_meeting_inform')
            response.body = json.dumps({'meeting_guid': self.meeting_guid,
                                        'organizer_jid': meeting["organizer_jid"],
                                        'start_date': time_to_str(meeting['start_date']),
                                        'end_date': time_to_str(meeting['end_date']),
                                        'room_id': meeting['room_id'],
                                        'temperature': meeting['temperature']
                                        })
            response.to = str(meeting['room_id'])
            await self.send(response)

            self.agent.meeting_room_calendars[meeting['room_id']].add_event(self.meeting_guid,
                                                                            meeting['start_date'],
                                                                            meeting['end_date'],
                                                                            meeting['temperature'])

            organizer_response = Message(to=meeting["organizer_jid"])
            organizer_response.set_metadata('performative', 'inform')
            organizer_response.set_metadata('type', 'meet_inform')
            organizer_response.body = json.dumps({'meeting_guid': self.meeting_guid,
                                                  'start_date': time_to_str(meeting['start_date']),
                                                  'end_date': time_to_str(meeting['end_date']),
                                                  'room_id': meeting['room_id'],
                                                  'temperature': meeting['temperature']
                                                  })
            await self.send(organizer_response)
            self.agent.processing_meeting = False
