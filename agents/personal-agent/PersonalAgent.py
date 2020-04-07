from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json


class PersonalAgent(Agent):
    @staticmethod
    def prepare_meet_request(self, date, temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'meet')
        msg.body = json.dumps({'date': date, 'temperature': temperature})
        return msg
    
    class SendReqBehav(CyclicBehaviour):
	async def run(self):
	    msg = PersonalAgent.prepare_meet_request(self,'jakas data',20,'central_agent')
	    await self.send(msg)
	    template = Template()
	    template.set_metadata('performative','inform')
	    template.set_metadata('type','meet')
	    #tu czekanie na template

    async def setup(self)
	sending = self.SendReqBehav()
	self.addbehaviour(sending)
