from spade.agent import Agent
from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message
from spade.template import Template
from sb_calendar import Calendar

import json
import time
import datetime
import sys
sys.path.insert(1, 'agents')
from energy import heat_balance, air_conditioner


class MeetingRoomAgent(Agent):
    personal_calendar = Calendar()
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
            agent.personal_calendar.add_event(msg_data.get('start_date'), msg_data.get('end_date'),
                                              msg_data.get('temperature'))

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
            new_time = datetime.datetime.strptime(msg_data['datetime'], "%Y-%m-%d %H:%M")
            self.agent.time_elapsed =  new_time - self.agent.last_time
            self.agent.energy_used = self.agent.ac_power * self.agent.time_elapsed.seconds
            self.agent.last_time = new_time
            heat_lost_per_second, heat_lost, temperature_lost = heat_balance(
                self.agent.time_elapsed, self.agent.temperature, self.agent.room_capacity, 
                self.agent.neighbors, self.agent.ac_power)
            self.agent.temperature -= temperature_lost
            #tu ustawianie temperatury
            heat_needed = air_conditioner(self.agent.temperature, 
                self.agent.TODO_temperatura_ktora_ma_byc, self.agent.room_capacity)
            heat_needed += heat_lost
            self.agent.ac_power += heat_needed / self.agent.TODO_czas_do_spotkania_w_sekundach / self.agent.ac_performance
            b = self.agent.SendEnergyUsageInformBehaviour()
            self.agent.add_behaviour(b)

    class SendEnergyUsageInformBehaviour(OneShotBehaviour):
        async def run(self):
            energy = self.agent.ac_power * self.agent.time_elapsed
            msg = MeetingRoomAgent.prepare_energy_usage_inform(self, energy, 'energy_agent')
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
        self.last_time = datetime.datetime.now()


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
