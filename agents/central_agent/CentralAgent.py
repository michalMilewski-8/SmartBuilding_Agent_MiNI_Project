from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json


class CentralAgent(Agent):

    def __init__(self):
        super.__init__()
        self.current_time = 0

    def setup(self):
        time_sync_template = Template()
        time_sync_template.set_metadata('type', 'datetime_inform')
        time_sync_template.set_metadata('performative', 'inform')
        self.add_behaviour(self.TimeSynchronizationBehaviour(), time_sync_template)

    # @staticmethod
    # def prepare_new_meeting_request(self, date, temperature, organizer_jid, receivers):
    #     msg = Message(to=receivers)
    #     msg.set_metadata('performative', 'request')
    #     msg.set_metadata('type', 'new_meeting')
    #     msg.body = json.dumps({'time': date, 'temperature': temperature, 'organizer_jid': organizer_jid})
    #     return msg
    #
    # @staticmethod
    # def prepare_power_data_request(self, receivers):
    #     msg = Message(to=receivers)
    #     msg.set_metadata('performative', 'request')
    #     msg.set_metadata('type', 'power_data')
    #     return msg
    #
    # @staticmethod
    # def prepare_room_booking_response(self, room_agent_jid, is_approved, receivers):
    #     msg = Message(to=receivers)
    #     msg.set_metadata('performative', 'inform')
    #     msg.set_metadata('type', 'new_meeting')
    #     msg.body = json.dumps({'room': room_agent_jid, 'approved': is_approved})
    #     return msg
    #
    # @staticmethod
    # def prepare_outdoor_temperature_request(self, date, receivers):
    #     msg = Message(to=receivers)
    #     msg.set_metadata('performative', 'request')
    #     msg.set_metadata('type', 'outdoor_temperature')
    #     msg.body = json.dumps({'date': date})
    #     return msg

    @staticmethod
    def prepare_meeting_score_request(self, receivers, guid, start, end, temperature):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'meeting_score_request')
        msg.body = json.dumps({'meeting-guid': guid, 'start_date': start, 'end_date': end, 'temperature': temperature})
        return msg

    async def find_best_room(self, behav, msg_guid, start_date, end_date, participants, organiser):
        print("find_best_room started")
        # do smth here

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

    # class OutdoorTempRequest(OneShotBehaviour):
    #
    #     def __init__(self, date):
    #         super().__init__()
    #         self.date = date
    #
    #     async def run(self):
    #         request = self.agent.prepare_outdoor_temperature_request(self.date, self.agent.outdoor_agent)
    #         await self.send(request)
    #         response = await self.receive(10)
    #         response_body = json.loads(response.body)
    #         if 'temperature' in response_body:
    #             self.agent.temperature(response_body['temperature'])
    #
    # class PowerDataRequest(OneShotBehaviour):
    #
    #     async def run(self):
    #         request = self.agent.prepare_power_data_request(self.agent.technical_agent)
    #         await self.send(request)
    #         response = await self.receive(10)
    #         response_body = json.loads(response.body)
    #         if 'power' in response_body:
    #             self.agent.power(response_body['power'])

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
                                               msg_body.get('end_date'), msg_body.get('participants'), msg.sender)
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

    class MeetingLateBehviour(CyclicBehaviour):

        async def run(self):
            msg = await self.receive()
            msg_body = json.dumps(msg.body)
