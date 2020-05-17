from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json


class CentralAgent(Agent):

    current_time = 0
    meeting_room_calendars = {}
    meeting_room_neighbours = {}

    @staticmethod
    def prepare_meeting_score_request(self, receivers, guid, start, end, temperature):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'meeting_score_request')
        msg.body = json.dumps({'meeting-guid': guid, 'start_date': start, 'end_date': end, 'temperature': temperature})
        return msg

    def setup(self):
        time_sync_template = Template()
        time_sync_template.set_metadata('type', 'datetime_inform')
        time_sync_template.set_metadata('performative', 'inform')
        self.add_behaviour(self.TimeSynchronizationBehaviour(), time_sync_template)
        meeting_request_template = Template()
        meeting_request_template.set_metadata('type', 'meet_request')
        meeting_request_template.set_metadata('performative', 'request')
        self.add_behaviour(self.MeetingBookingBehaviour(), meeting_request_template)
        meeting_score_template = Template()
        meeting_score_template.set_metadata('type', 'meeting_score_inform')
        meeting_score_template.set_metadata('performative', 'inform')
        self.add_behaviour(ReceiveScoreBehaviour, meeting_score_template)

    async def find_best_room(self, msg_guid, start_date, end_date, participants, organiser, temp):
        print("find_best_room started")

        room = min(self.meeting_room_calendars.keys(), key=lambda x: self.calculate_points(start_date, end_date,
                                                                                           temp, x))
        return {'start_date': start_date, 'end_date': end_date, 'room_id': room}

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
        move_meeting_propose.body = json.loads({'meeting_guid': msg_guid, 'start_date': best_start_date,
                                                'end_date': best_end_date})
        await behav.send(move_meeting_propose)

    async def negotiate_end(self, behav, msg_guid, start_date, end_date,
                            receiver, delete_meeting):
        move_meeting_inform = Message(to=receiver)
        move_meeting_inform.set_metadata('performative', 'inform')
        move_meeting_inform.set_metadata('type', 'move_meeting_inform')
        move_meeting_inform.body = json.loads({'meeting_guid': msg_guid, 'start_date': start_date,
                                               'end_date': end_date, "delete_meeting": delete_meeting})
        await behav.send(move_meeting_inform)

    async def late_confirm(self, behav, confirmed, receiver):
        late_confirm = Message(to=receiver)
        late_confirm.set_metadata('performative', 'inform')
        late_confirm.set_metadata('type', 'move_meeting_inform')
        late_confirm.body = json.loads({"confirmed": confirmed})
        await behav.send(late_confirm)

    class TimeSynchronizationBehaviour(CyclicBehaviour):

        async def run(self):
            msg = await self.receive()
            msg_body = json.dumps(msg.body)
            if 'datetime' in msg_body:
                self.agent.current_time = msg_body['datetime']

    class MeetingBookingBehaviour(CyclicBehaviour):

        async def run(self):
            msg = await self.receive()
            msg_body = json.dumps(msg.body)
            result = self.agent.find_best_room(self, msg_body.get('meeting_guid'), msg_body.get('start_date'),
                                               msg_body.get('end_date'), msg_body.get('participants'), msg.sender,
                                               msg_body.get('temperature'))
            response = Message()
            response.set_metadata('performative', 'inform')
            response.set_metadata('type', 'new_meeting_inform')
            response.body = json.loads({'meeting_guid': msg_body.get('meeting_guid'),
                                        'organizer_jid': msg.sender,
                                        'start_date': result.get('start_date'),
                                        'end_date': result.get('end_date'),
                                        'room_id': result.get('room_id'),
                                        'temperature': msg_body.get('temperature')
                                        })

            for receiver in msg_body.get('participants'):
                response.to = receiver
                await self.send(response)

            response.to = result['room_id']
            await self.send(response)

            organizer_response = Message(to=msg.sender)
            organizer_response.set_metadata('performative', 'inform')
            organizer_response.set_metadata('type', 'meet_inform')
            organizer_response.body = json.loads({'meeting_guid': msg_body.get('meeting_guid'),
                                                  'start_date': result.get('start_date'),
                                                  'end_date': result.get('end_date'),
                                                  'room_id': result.get('room_id'),
                                                  })
            await self.send(organizer_response)

    class MeetingLateBehaviour(CyclicBehaviour):

        async def run(self):
            msg = await self.receive()
            msg_body = json.dumps(msg.body)

    class ReceiveScoreBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout = 1)
            if msg:
                print('received score')
                #do smth useful
            