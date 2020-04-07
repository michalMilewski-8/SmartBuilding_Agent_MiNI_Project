from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json


class TechnicalAgent(Agent):

    @staticmethod
    def prepare_power_data_response(self, power, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'power_data')
        msg.body = json.dumps({'power': power})
        return msg

    @staticmethod
    def prepare_room_power_exchange(self, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'room_power_data')
        return msg

    def get_power(self):
        return self.power

    def add_to_power(self, power):
        self.power += power

    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.power = 0
        self.time_speed = 1
        self.known_rooms = []

    def setup(self):
        room_response_template = Template()
        room_response_template.set_metadata('performative', 'inform')
        room_response_template.set_metadata('type', 'room_power_data')

        room_request_template = Template()
        room_request_template.set_metadata('performative', 'request')
        room_request_template.set_metadata('type', 'power_data')

        self.add_behaviour(self.PowerDataExchangeBehaviour(), room_request_template)
        self.add_behaviour(self.GetRoomPowerBehaviour(60/self.time_speed), room_response_template)

    class PowerDataExchangeBehaviour(CyclicBehaviour):

        async def run(self):
            msg = await self.receive()
            response = self.agent.prepare_power_data_response(self.agent.get_power(), msg.sender)

    class GetRoomPowerBehaviour(PeriodicBehaviour):

        async def run(self):
            for room in self.agent.known_rooms:
                msg = self.agent.prepare_room_power_exchange(room)
                await self.send(msg)
            for room in self.agent.known_rooms:
                response = await self.receive(10)
                response_body = json.loads(response.body)
                if 'power' in response_body:
                    self.agent.add_to_power(response_body['power'])



