from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json


class RoomAgent(Agent):
    @staticmethod
    def prepare_room_data_exchange_request(self, temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'room_data_exchange')
        msg.body = json.dumps({'temperature': temperature})
        return msg

    @staticmethod
    def prepare_room_data_exchange_response(self, temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'room_data_exchange')
	msg.body = json.dumps({'temperature': temperature})
        return msg

    @staticmethod
    def prepare_room_data_request(self,receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'room_data')
        return msg

    @staticmethod
    def prepare_room_data_response(self, temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'room_data')
        msg.body = json.dumps({'temperature': temperature})
        return msg

    @staticmethod
    def prepare_outdoor_temperature_request(self, date, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'outdoor_temperature')
        msg.body = json.dumps({'date': date})
        return msg

    @staticmethod
    def prepare_room_power_response(self, power, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'room_power')
        msg.body = json.dumps({'power': power})
        return msg
