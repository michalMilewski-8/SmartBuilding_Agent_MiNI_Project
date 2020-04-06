from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json


class PersonalAgent(Agent):
    @staticmethod
    def prepare_meet_request_request(self, date, temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'meet_request')
        msg.body = json.dumps({'date': date, 'temperature': temperature})
        return msg
