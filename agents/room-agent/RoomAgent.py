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


    async def setup(self)
	power = self.PowerResponseBehav()
	power_template = Template()
	power_template.set_metadata('performative','request')
	power_template.set_metadata('type','room_power')
	self.add_behaviour(power,power_template)
	exchange_response = self.ExchangeResponseBehav()
	exchange_response_template = Template()
	exchange_response_template.set_metadata('performative','request')
	exchange_response_template.set_metadata('type','room_data_exchange')
	self.add_behaviour(exchange_response,exchange_response_template)
	room_data_response = self.RoomDataResponseBehav()
	room_data_response_template = Template()
	room_data_response_template.set_metadata('performative','request')
	room_data_response_template.set_metadata('type','room_data')
	self.add_behaviour(room_data_response,room_data_response_template)
	room_data_request = self.RoomDataRequestBehav()
	self.add_behaviour(room_data_request)
	room_data_exchange_request = self.RoomDataExchangeRequestBehav()
	self.add_behaviour(room_data_exchange_request)
	outdoor_temperature_request = self.OutdoorTemperatureRequestBehav()
	self.add_behaviour(outdoor_temperature_request)


    class RoomDataRequestBehav(CyclicBehaviour):
	async def run(self):
	    msg = RoomAgent.prepare_room_data_request(self,'inny_room_agent')
	    await self.send(msg)
	    template = Template()
	    template.set_metadata('performative','inform')
	    template.set_metadata('type','room_data')
	    #tu czekanie na template

    class RoomDataExchangeRequestBehav(CyclicBehaviour):
	async def run(self):
	    msg = RoomAgent.prepare_room_data_exchange_request(self,20,'inny_room_agent')
	    await self.send(msg)
	    template = Template()
	    template.set_metadata('performative','inform')
	    template.set_metadata('type','room_data_exchange')
	    #tu czekanie na template

    class OutdoorTemperatureRequestBehav(CyclicBehaviour):
	async def run(self):
	    msg = RoomAgent.prepare_outdoor_temperature_request(self,'jakas data','inny_room_agent')
	    await self.send(msg)
	    template = Template()
	    template.set_metadata('performative','inform')
	    template.set_metadata('type','outdoor_temperature')
	    #tu czekanie na template

    class PowerResponseBehav(CyclicBehaviour):
	async def run(self):
	    msg = await self.receive()
	    msg_data = json.loads(msg.body)
	    response = prepare_room_power_response(self,'10 MW',msg.sender)
	    await self.send(response)

    class ExchangeResponseBehav(CyclicBehaviour):
	async def run(self):
	    msg = await self.receive()
	    msg_data = json.loads(msg.body)
	    response = prepare_room_data_exchange_response(self,20,msg.sender)
	    await self.send(response)

    class RoomDataResponseBehav(CyclicBehaviour):
	async def run(self):
	    msg = await self.receive()
	    msg_data = json.loads(msg.body)
	    response = prepare_room_data_response(self,20,msg.sender)
	    await self.send(response)





