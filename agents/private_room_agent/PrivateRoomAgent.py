from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json
import time
from datetime import datetime

class PrivateRoomAgent(Agent):

    preferred_temperature = 20
    outdoor_agent = "outdoor_agent"
    energy_agent = 'energy_agent'

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
                self.agent.date = msg_data["datetime"]
                print(str(self.agent.jid) + " current date: {}".format(self.agent.date))

    class SendEnergyUsageInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = agent.prepare_energy_usage_inform(self, 20, agent.energy_agent)
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

    async def setup(self):
        print(str(self.jid) + " Private room agent setup")
        self.date = datetime.now()
        
        datetime_inform_template = Template()
        datetime_inform_template.set_metadata('performative','inform')
        datetime_inform_template.set_metadata("type","datetime_inform")
        datetimeBehaviour = self.ReceiveDatetimeInformBehaviour()
        self.add_behaviour(datetimeBehaviour,datetime_inform_template)

        preferences_inform_template = Template()
        preferences_inform_template.set_metadata('performative', 'inform')
        preferences_inform_template.set_metadata('type', 'preferences')
        preferences = self.ReceivePreferencesInformBehaviour()
        self.add_behaviour(preferences, preferences_inform_template)


        send_room_data_exchange_request_behaviour = self.SendRoomDataExchangeRequestBehaviour(period = 10)
        self.add_behaviour(send_room_data_exchange_request_behaviour)

        room_data_exchange_request_template = Template()
        room_data_exchange_request_template.set_metadata('performative','request')
        room_data_exchange_request_template.set_metadata('type','room_data_exchange_request')
        receive_room_data_exchange_request_behaviour = self.ReceiveRoomDataExchangeRequestBehaviour()
        self.add_behaviour(receive_room_data_exchange_request_behaviour,room_data_exchange_request_template)

        room_data_inform_template = Template()
        room_data_inform_template.set_metadata('performative','inform')
        room_data_inform_template.set_metadata('type','room_data_inform')
        receive_room_data_inform_behaviour = self.ReceiveRoomDataInformBehaviour()
        self.add_behaviour(receive_room_data_inform_behaviour,room_data_inform_template)

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
