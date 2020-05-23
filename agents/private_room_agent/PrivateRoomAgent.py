from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json
import time

from datetime import datetime
import sys
from ..energy import heat_balance, air_conditioner

class PrivateRoomAgent(Agent):

    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.personal_calendar = Calendar()
        self.score_request_dict = {}
        self.central = ""
        self.neighbours = []
	self.people = []
        self.temperature = 20
        self.temperatures = {}
	self.preferred_temperature = 20
    	self.outdoor_agent = ""
    	self.energy_agent = ""

    @staticmethod
    def prepare_room_data_exchange_request(self, temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'room_data_exchange_request')
        msg.body = json.dumps({'temperature': temperature})
        return msg

    @staticmethod
    def prepare_room_data_inform(self, temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'room_data_inform')
        msg.body = json.dumps({'temperature': temperature})
        return msg

    @staticmethod
    def prepare_energy_usage_inform(self, energy, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'energy_usage')
        msg.body = json.dumps({'energy_used_since_last_message': energy})
        return msg

    @staticmethod
    def prepare_outdoor_temperature_request(self, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'outdoor_temperature')
        msg.body = json.dumps({})
        return msg

    @staticmethod
    def prepare_temperature_at_inform(self, receivers, guid, temperature):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'temperature_at_inform')
        msg.body = json.dumps({'request-guid': guid, 'temperature': temperature})
        return msg

    outdoor_temperature_inform_template = Template()
    outdoor_temperature_inform_template.set_metadata('performative','inform')
    outdoor_temperature_inform_template.set_metadata('type','outdoor_temperature')


    class ReceiveRoomDataExchangeRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout = 1)
            if msg:
                msg_data = json.loads(msg.body)
                self.agent.temperatures[msg.sender] = msg_data["temperature"]
                print(str(self.agent.jid) + " received exchange request from " + str(msg.sender) + " with " + str(msg_data["temperature"]))
                msg2 = PrivateRoomAgent.prepare_room_data_inform(self, self.agent.temperature, str(msg.sender))
                print(str(self.agent.jid) + " sending exchange inform to " + str(msg.sender) + " with " + str(self.agent.temperature))
                await self.send(msg2)

    class ReceiveRoomDataInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout = 1)
            if msg:
                msg_data = json.loads(msg.body)
                self.agent.temperatures[msg.sender] = msg_data["temperature"]
                print(str(self.agent.jid) + " received exchange inform from " + str(msg.sender) + " with " + str(msg_data["temperature"]))


    class SendRoomDataExchangeRequestBehaviour(PeriodicBehaviour):
        async def run(self):
            for neighbour in self.agent.neighbours:
                if neighbour < str(self.agent.jid):
                    msg = PrivateRoomAgent.prepare_room_data_exchange_request(self, self.agent.temperature, neighbour)
                    print(str(self.agent.jid) + " sending exchange request to " + neighbour + " with " + str(self.agent.temperature))
                    await self.send(msg)

    class ReceiveDatetimeInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout = 1)
            if msg:
              msg_data = json.loads(msg.body)
              new_time = datetime.strptime(msg_data['datetime'], "%Y-%m-%d %H:%M")
              self.agent.date = new_time
              print(str(self.agent.jid) + " current date: {}".format(self.agent.date))
              self.agent.time_elapsed =  new_time - self.agent.last_time
              self.agent.energy_used = self.agent.ac_power * self.agent.time_elapsed.seconds
              self.agent.last_time = new_time
              heat_lost_per_second, heat_lost, temperature_lost = heat_balance(
                  self.agent.time_elapsed, self.agent.temperature, self.agent.room_capacity, 
                  self.agent.temperatures, self.agent.ac_power)
              self.agent.temperature -= temperature_lost
              #tu ustawianie temperatury
              heat_needed = air_conditioner(self.agent.temperature, 
                  self.agent.TODO_temperatura_ktora_ma_byc, self.agent.room_capacity)
              heat_needed += heat_lost
              self.agent.ac_power += heat_needed / self.agent.TODO_czas_do_spotkania_w_sekundach / self.agent.ac_performance
              b = self.agent.SendEnergyUsageInformBehaviour()
              self.agent.add_behaviour(b)

    class SendEnergyUsageInformBehaviour(CyclicBehaviour):
        async def run(self):
            energy = self.agent.ac_power * self.agent.time_elapsed
            msg = agent.prepare_energy_usage_inform(self, energy, agent.energy_agent)
            await self.send(msg)

    class SendOutdoorTemperatureRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = agent.prepare_outdoor_temperature_request(self, agent.outdoor_agent)
            await self.send(msg)
            # czekanie na inform

    class ReceivePreferencesInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            if msg:
                msg_data = (json.loads(msg.body))
                if "optimal_temperature" in msg_data:
                    print("Optimal temperature: {}".format(msg_data.get("optimal_temperature")))
                    agent.preferred_temperature = msg_data.get("optimal_temperature")

    class ReceiveTemperatureAtRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout = 1)
            if msg:
                msg_data = json.loads(msg.body)
                temp = self.agent.personal_calendar.get_temperature_at(msg_data["date"])
                msg2 = PrivateRoomAgent.prepare_temperature_at_inform(msg.sender, msg_data["request_guid"], temp)
                await self.send(msg2)

    async def setup(self):
        print(str(self.jid) + " Private room agent setup")
        self.date = datetime.now()
        
        datetime_inform_template = Template()
        datetime_inform_template.set_metadata('performative', 'inform')
        datetime_inform_template.set_metadata("type", "datetime_inform")
        datetimeBehaviour = self.ReceiveDatetimeInformBehaviour()
        self.add_behaviour(datetimeBehaviour, datetime_inform_template)

        preferences_inform_template = Template()
        preferences_inform_template.set_metadata('performative', 'inform')
        preferences_inform_template.set_metadata('type', 'preferences')
        preferences = self.ReceivePreferencesInformBehaviour()
        self.add_behaviour(preferences, preferences_inform_template)
        temperature_at_inform_template = Template()
        temperature_at_inform_template.set_metadata('performative', 'inform')
        temperature_at_inform_template.set_metadata('type', 'temperature_at_inform')
        self.add_behaviour(self.ReceiveTemperatureAtInformBehaviour(), temperature_at_inform_template)
        send_room_data_exchange_request_behaviour = self.SendRoomDataExchangeRequestBehaviour(period=10)
        self.add_behaviour(send_room_data_exchange_request_behaviour)

        room_data_exchange_request_template = Template()
        room_data_exchange_request_template.set_metadata('performative', 'request')
        room_data_exchange_request_template.set_metadata('type', 'room_data_exchange_request')
        receive_room_data_exchange_request_behaviour = self.ReceiveRoomDataExchangeRequestBehaviour()
        self.add_behaviour(receive_room_data_exchange_request_behaviour, room_data_exchange_request_template)

        room_data_inform_template = Template()
        room_data_inform_template.set_metadata('performative', 'inform')
        room_data_inform_template.set_metadata('type', 'room_data_inform')
        receive_room_data_inform_behaviour = self.ReceiveRoomDataInformBehaviour()
        self.add_behaviour(receive_room_data_inform_behaviour, room_data_inform_template)

if __name__ == "__main__":
    agent = PrivateRoomAgent("private_room@localhost", "private_room")
    agent.start()

    # wait until user interrupts with ctrl+C
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    agent.stop()
