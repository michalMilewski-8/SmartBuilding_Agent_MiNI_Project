from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
from ..sb_calendar import Calendar
import json
from datetime import datetime


class CentralAgent(Agent):
    date = None
    meeting_room_calendars = {}
    meeting_room_neighbours = {}
    meetings_info = {}  # example {"date_start": start_date, "date_end": end_date,

    #           "temperature": temp, "scores": {room_jid:score}}

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
        print('dodalem behav')
        print(self.behaviours)

        meeting_score_template = Template()
        meeting_score_template.set_metadata('type', 'meeting_score_inform')
        meeting_score_template.set_metadata('performative', 'inform')
        self.add_behaviour(self.ReceiveScoreBehaviour(), meeting_score_template)

    async def find_best_room(self, agent, meet_guid, start_date, end_date, temp):
        print("find_best_room started")

        for meeting_room in agent.meeting_room_calendars.keys():
            score_request = Message(to=meeting_room)
            score_request.set_metadata("performative", "request")
            score_request.set_metadata("type", "meeting_score_request")
            score_request.body = json.dumps({"meeting_guid": meet_guid,
                                             "start_date": start_date,
                                             "end_date": end_date,
                                             "temperature": temp
                                             })
            await self.send(score_request)

    def calculate_points(self, start_date, end_date, temp, room):
        result = 0
        result += self.meeting_room_calendars[room].calculate_points(start_date, end_date, temp)
        for neigh in self.meeting_room_neighbours[room]:
            result += self.meeting_room_calendars[neigh].calculate_points_as_neighbour(start_date, end_date, temp)
        return result

    async def negotiate(self, behav, msg_guid, best_start_date, best_end_date,
                        receiver):
        move_meeting_propose = Message(to=receiver)
        move_meeting_propose.set_metadata('performative', 'propose')
        move_meeting_propose.set_metadata('type', 'move_meeting_propose')
        move_meeting_propose.body = json.dumps({'meeting_guid': msg_guid, 'start_date': best_start_date,
                                                'end_date': best_end_date})
        await behav.send(move_meeting_propose)

    async def negotiate_end(self, behav, msg_guid, start_date, end_date,
                            receiver, delete_meeting):
        move_meeting_inform = Message(to=receiver)
        move_meeting_inform.set_metadata('performative', 'inform')
        move_meeting_inform.set_metadata('type', 'move_meeting_inform')
        move_meeting_inform.body = json.dumps({'meeting_guid': msg_guid, 'start_date': start_date,
                                               'end_date': end_date, "delete_meeting": delete_meeting})
        await behav.send(move_meeting_inform)

    async def late_confirm(self, behav, confirmed, receiver):
        late_confirm = Message(to=receiver)
        late_confirm.set_metadata('performative', 'inform')
        late_confirm.set_metadata('type', 'move_meeting_inform')
        late_confirm.body = json.dumps({"confirmed": confirmed})
        await behav.send(late_confirm)

    class ReceiveDatetimeInformBehaviour(CyclicBehaviour):
        async def run(self):
            print("smth")
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                self.agent.date = msg_data["datetime"]
                print(str(self.agent.jid) + " current date: {}".format(self.agent.date))

    class MeetingBookingBehaviour(CyclicBehaviour):
        async def run(self):
            print('waiting for new meeting')
            msg = await self.receive(timeout=1)
            print('waiting for new meeting')
            if msg:
                print(msg)
                msg_body = json.loads(msg.body)
                self.agent.meetings_info[msg_body.get('meeting_guid')] = {'meeting_guid': msg_body.get('meeting_guid'),
                                                                          'organizer_jid': msg.sender,
                                                                          'start_date': msg_body.get('start_date'),
                                                                          'end_date': msg_body.get('end_date'),
                                                                          'room_id': None,
                                                                          'temperature': msg_body.get('temperature'),
                                                                          "participants": msg_body.get('participants')}

                self.agent.find_best_room(self, self.agent, msg_body.get('meeting_guid'),
                                          msg_body.get('start_date'),
                                          msg_body.get('end_date'), msg_body.get('temperature'))

    class MeetingLateBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_body = json.loads(msg.body)

    class ReceiveScoreBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                print('received score')
                msg_body = json.loads(msg.body)
                self.agent.meetings_info[msg_body["meeting_guid"]]["scores"][msg.sender] = msg_body["score"]
                if self.agent.meetings_info[msg_body["meeting_guid"]][
                    "scores"].count() == self.agent.meeting_room_calendars.keys().count():
                    behav = self.agent.RespondForMeetingRequest()
                    behav.meeting_guid = msg_body["meeting_guid"]
                    self.agent.add_behaviour()

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

            response = Message()
            response.set_metadata('performative', 'inform')
            response.set_metadata('type', 'new_meeting_inform')
            response.body = json.dumps({'meeting_guid': self.meeting_guid,
                                        'organizer_jid': meeting["organizer"],
                                        'start_date': meeting.get('start_date'),
                                        'end_date': meeting.get('end_date'),
                                        'room_id': meeting.get('room_id'),
                                        'temperature': meeting.get('temperature')
                                        })

            for receiver in meeting.get('participants'):
                response.to = receiver
                await self.send(response)

            response.to = meeting['room_id']
            await self.send(response)

            organizer_response = Message(to=meeting["organizer"])
            organizer_response.set_metadata('performative', 'inform')
            organizer_response.set_metadata('type', 'meet_inform')
            organizer_response.body = json.dumps({'meeting_guid': self.meeting_guid,
                                                  'start_date': meeting.get('start_date'),
                                                  'end_date': meeting.get('end_date'),
                                                  'room_id': meeting.get('room_id'),
                                                  })
            await self.send(organizer_response)
