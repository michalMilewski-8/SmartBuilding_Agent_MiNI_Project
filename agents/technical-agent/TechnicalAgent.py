from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
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
