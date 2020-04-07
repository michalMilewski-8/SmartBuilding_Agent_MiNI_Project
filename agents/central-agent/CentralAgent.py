from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json


class CentralAgent(Agent):
    @staticmethod
    def prepare_new_meeting_request(self, date, temperature, organizer_jid, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'new_meeting')
        msg.body = json.dumps({'time': date, 'temperature': temperature, 'organizer_jid': organizer_jid})
        return msg

    @staticmethod
    def prepare_power_data_request(self, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'power_data')
        return msg

    @staticmethod
    def prepare_room_booking_response(self, room_agent_jid, is_approved, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'new_meeting')
        msg.body = json.dumps({'room': room_agent_jid, 'approved': is_approved})
        return msg

    @staticmethod
    def prepare_outdoor_temperature_request(self, date, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'outdoor_temperature')
        msg.body = json.dumps({'date': date})
        return msg

    class OutdoorTempRequest(OneShotBehaviour):

        def __init__(self, date):
            super().__init__()
            self.date = date

        async def run(self):
            request = self.agent.prepare_outdoor_temperature_request(self.date, self.agent.outdoor_agent)
            await self.send(request)
            response = await self.receive(10)
            response_body = json.loads(response.body)
            if 'temperature' in response_body:
                self.agent.temperature(response_body['temperature'])

    class PowerDataRequest(OneShotBehaviour):

        async def run(self):
            request = self.agent.prepare_power_data_request(self.agent.technical_agent)
            await self.send(request)
            response = await self.receive(10)
            response_body = json.loads(response.body)
            if 'power' in response_body:
                self.agent.power(response_body['power'])