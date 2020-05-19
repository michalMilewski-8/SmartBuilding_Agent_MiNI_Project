from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
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
        msg.set_metadata('type', 'room_data_exchange')
        msg.body = json.dumps({'temperature': temperature})
        return msg

    @staticmethod
    def prepare_room_data_inform(self, temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'room_data')
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

    room_data_exchange_request_template = Template()
    room_data_exchange_request_template.set_metadata('performative', 'request')
    room_data_exchange_request_template.set_metadata('type', 'room_data_exchange')

    room_data_inform_template = Template()
    room_data_inform_template.set_metadata('performative', 'inform')
    room_data_inform_template.set_metadata('type', 'room_data')

    outdoor_temperature_inform_template = Template()
    outdoor_temperature_inform_template.set_metadata('performative', 'inform')
    outdoor_temperature_inform_template.set_metadata('type', 'outdoor_temperature')

    class ReceiveRoomDataExchangeRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)
            # wyslanie room_data_inform

    class SendRoomDataExchangeRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = agent.prepare_room_data_exchange_request(self, 20, 'another_room_agent')
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
