from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json
import time

class MeetingRoomAgent(Agent):
    @staticmethod
    def prepare_room_data_exchange_request(self, temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'room_data_exchange')
        msg.body = json.dumps({'temperature' : temperature})
        return msg

    @staticmethod
    def prepare_room_data_inform(self, temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'room_data')
        msg.body = json.dumps({'temperature' : temperature})
        return msg

    @staticmethod
    def prepare_energy_usage_inform(self, energy, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'energy_usage')
        msg.body = json.dumps({'energy_used_since_last_message' : energy})
        return msg

    @staticmethod
    def prepare_outdoor_temperature_request(self, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'outdoor_temperature')
        msg.body = json.dumps({})
        return msg

    @staticmethod
    def prepare_temperature_at_request(self, receivers, guid, date):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'temperature_at_request')
        msg.body = json.dumps({'request-guid': guid, 'date': date})
        return msg

    @staticmethod
    def prepare_temperature_at_inform(self, receivers, guid, temperature):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'temperature_at_inform')
        msg.body = json.dumps({'request-guid': guid, 'temperature': temperature})
        return msg

    @staticmethod
    def prepare_meeting_score_inform(self, receivers, guid, score):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'meeting_score_inform')
        msg.body = json.dumps({'meeting-guid': guid, 'score': score})
        return msg


    new_meeting_inform_template = Template()
    new_meeting_inform_template.set_metadata('performative','inform')
    new_meeting_inform_template.set_metadata('type','new_meeting')

    room_data_exchange_request_template = Template()
    room_data_exchange_request_template.set_metadata('performative','request')
    room_data_exchange_request_template.set_metadata('type','room_data_exchange')

    room_data_inform_template = Template()
    room_data_inform_template.set_metadata('performative','inform')
    room_data_inform_template.set_metadata('type','room_data')

    datetime_inform_template = Template()
    datetime_inform_template.set_metadata('performative','inform')
    datetime_inform_template.set_metadata('type','datetime')

    outdoor_temperature_inform_template = Template()
    outdoor_temperature_inform_template.set_metadata('performative','inform')
    outdoor_temperature_inform_template.set_metadata('type','outdoor_temperature')

    move_meeting_inform_template = Template()
    move_meeting_inform_template.set_metadata('performative','inform')
    move_meeting_inform_template.set_metadata('type','move_meeting')


    class ReceiveNewMeetingInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)

    class ReceiveRoomDataExchangeRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)

    class SendRoomDataExchangeRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = MeetingRoomAgent.prepare_room_data_exchange_request(self, 20, 'another_room_agent')
            await self.send(msg)

    class ReceiveDatetimeInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)

    class SendEnergyUsageInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = MeetingRoomAgent.prepare_energy_usage_inform(self, 20, 'energy_agent')
            await self.send(msg)

    class SendOutdoorTemperatureRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = MeetingRoomAgent.prepare_outdoor_temperature_request(self, 'outdoor_agent')
            await self.send(msg)

    class ReceiveMoveMeetingInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)

    async def setup(self):
        print("Meeting room agent setup")

if __name__ == "__main__":
    agent = MeetingRoomAgent("meeting_room@localhost", "meeting_room")
    agent.start()

    # wait until user interrupts with ctrl+C
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    agent.stop()
