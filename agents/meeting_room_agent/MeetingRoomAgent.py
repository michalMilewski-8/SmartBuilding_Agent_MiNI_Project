from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import PeriodicBehaviour
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from ..sb_calendar import Calendar
from ..time_conversion import time_to_str, str_to_time

import json
import time
from datetime import datetime
import sys
from ..energy import heat_balance, air_conditioner

boundary_up = 25
boundary_down = 16


class MeetingRoomAgent(Agent):

    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.personal_calendar = Calendar()
        self.score_request_dict = {}
        self.central = ""
        self.neighbours = {}
        self.temperature = 20
        self.temperatures = {}
        self.date = datetime.now()
        self.ac_power = 0
        self.room_capacity = 200
        self.ac_performance = 1
        self.outdoor_wall = 20
        self.outdoor_temperature = self.temperature
        self.outdoor_agent = ""
        self.energy_agent = ""

    @staticmethod
    def prepare_room_data_exchange_request(temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'room_data_exchange_request')
        msg.body = json.dumps({'temperature': temperature})
        return msg

    @staticmethod
    def prepare_room_data_inform(temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'room_data_inform')
        msg.body = json.dumps({'temperature': temperature})
        return msg

    @staticmethod
    def prepare_energy_usage_inform(energy, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'energy_usage_inform')
        msg.body = json.dumps({'energy_used_since_last_message': energy})
        return msg

    @staticmethod
    def prepare_outdoor_temperature_request(receivers, date):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'outdoor_temperature')
        msg.body = json.dumps({'date': time_to_str(date)})
        return msg

    @staticmethod
    def prepare_temperature_at_request(receivers, guid, date):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'temperature_at_request')
        msg.body = json.dumps({'request_guid': guid, 'date': time_to_str(date)})
        return msg

    @staticmethod
    def prepare_temperature_at_inform(receivers, guid, temperature):
        msg = Message(to=str(receivers))
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'temperature_at_inform')
        msg.body = json.dumps({'request_guid': guid, 'temperature': temperature})
        return msg

    @staticmethod
    def prepare_meeting_score_inform(receivers, guid, score):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'meeting_score_inform')
        msg.body = json.dumps({'meeting_guid': guid, 'score': score})
        return msg

    new_meeting_inform_template = Template()
    new_meeting_inform_template.set_metadata('performative', 'inform')
    new_meeting_inform_template.set_metadata('type', 'new_meeting_inform')

    outdoor_temperature_inform_template = Template()
    outdoor_temperature_inform_template.set_metadata('performative', 'inform')
    outdoor_temperature_inform_template.set_metadata('type', 'outdoor_temperature_inform')

    move_meeting_inform_template = Template()
    move_meeting_inform_template.set_metadata('performative', 'inform')
    move_meeting_inform_template.set_metadata('type', 'move_meeting_inform')

    class ReceiveNewMeetingInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                print(msg)
                msg_data = json.loads(msg.body)
                self.agent.personal_calendar.add_event(msg_data['meeting_guid'],
                                                       str_to_time(msg_data['start_date']),
                                                       str_to_time(msg_data['end_date']),
                                                       msg_data['temperature'])

    class ReceiveRoomDataExchangeRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                temperature = msg_data["temperature"]
                self.agent.neighbours[str(msg.sender)]["temperature"] = temperature
                # print(str(self.agent.jid) + " received exchange request from " + str(msg.sender) + " with " + str(self.agent.neighbours[str(msg.sender)]["temperature"]))
                msg2 = MeetingRoomAgent.prepare_room_data_inform(self.agent.temperature, str(msg.sender))
                # print(str(self.agent.jid) + " sending exchange inform to " + str(msg.sender) + " with " + str(self.agent.temperature))
                await self.send(msg2)

    class ReceiveRoomDataInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                self.agent.neighbours[str(msg.sender)]["temperature"] = msg_data["temperature"]
                # print(str(self.agent.jid) + " received exchange inform from " + str(msg.sender) + " with " + str(self.agent.neighbours[str(msg.sender)]["temperature"]))

    class SendRoomDataExchangeRequestBehaviour(OneShotBehaviour):
        async def run(self):
            for neighbour in self.agent.neighbours:
                if neighbour < str(self.agent.jid):
                    msg = MeetingRoomAgent.prepare_room_data_exchange_request(self.agent.temperature, neighbour)
                    # print(str(self.agent.jid) + " sending exchange request to " + neighbour + " with " + str(self.agent.temperature))
                    await self.send(msg)

    class ReceiveDatetimeInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                new_time = str_to_time(msg_data['datetime'])
                last_time = self.agent.date
                self.agent.date = new_time
                # print(str(self.agent.jid) + " current date: {}".format(self.agent.date))
                time_elapsed = new_time - last_time
                b = self.agent.SendEnergyUsageInformBehaviour()
                b.set_energy(abs(self.agent.ac_power * time_elapsed.seconds))
                self.agent.add_behaviour(b)

                if time_elapsed.seconds > 0:
                    energy_used = self.agent.ac_power * time_elapsed.seconds
                    heat_lost_per_second, heat_lost, temperature_lost = heat_balance(
                        time_elapsed, self.agent.temperature, self.agent.room_capacity,
                        self.agent.neighbours, self.agent.ac_power,
                        self.agent.outdoor_wall,
                        self.agent.outdoor_temperature)
                    print(str(self.agent.jid) + " temp " + str(self.agent.temperature))
                    self.agent.temperature -= temperature_lost

                    next_meeting_time, temperature_at_next_meeting = self.agent.personal_calendar.get_proximity_peek(
                        self.agent.date, time_elapsed.seconds)
                    heat_needed = 0
                    if temperature_at_next_meeting is None:
                        if self.agent.temperature < boundary_down:
                            heat_needed = air_conditioner(self.agent.temperature,
                                                          boundary_down, self.agent.room_capacity)
                        elif self.agent.temperature > boundary_up:
                            heat_needed = air_conditioner(self.agent.temperature,
                                                          boundary_up, self.agent.room_capacity)
                    else:
                        heat_needed = air_conditioner(self.agent.temperature,
                                                      temperature_at_next_meeting, self.agent.room_capacity)

                    if next_meeting_time is not None and time_elapsed.seconds > (next_meeting_time - self.agent.date).seconds:
                        diff = next_meeting_time - self.agent.date
                        self.agent.ac_power = heat_needed / diff.seconds / self.agent.ac_performance
                    else:
                        self.agent.ac_power = heat_needed / time_elapsed.seconds / self.agent.ac_performance

                b2 = self.agent.SendRoomDataExchangeRequestBehaviour()
                self.agent.add_behaviour(b2)
                b3 = self.agent.SendOutdoorTemperatureRequestBehaviour()
                self.agent.add_behaviour(b3)

    class SendEnergyUsageInformBehaviour(OneShotBehaviour):
        def __init__(self):
            super().__init__()
            self.energy = 0

        def set_energy(self, energy):
            self.energy = energy

        async def run(self):
            msg = self.agent.prepare_energy_usage_inform(self.energy, self.agent.energy_agent)
            await self.send(msg)

    class SendOutdoorTemperatureRequestBehaviour(OneShotBehaviour):
        async def run(self):
            msg = self.agent.prepare_outdoor_temperature_request(self.agent.outdoor_agent, self.agent.date)
            await self.send(msg)

    class ReceiveMoveMeetingInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)

    #         TODO(michal) implement this method

    class ReceiveMeetingScoreRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                # print(msg)
                msg_data = json.loads(msg.body)
                date_from = str_to_time(msg_data["start_date"])
                date_to = str_to_time(msg_data["end_date"])
                if not self.agent.personal_calendar.is_free(date_from, date_to):
                    await self.send(
                        self.agent.prepare_meeting_score_inform(self.agent.central, msg_data["meeting_guid"], None))
                else:
                    new_score = {
                        "date_from": date_from,
                        "date_to": date_to,
                        "temperature": msg_data["temperature"],
                        "temperatures": []
                    }
                    self.agent.score_request_dict[msg_data["meeting_guid"]] = new_score
                    for neighbour in self.agent.neighbours:
                        msg2 = self.agent.prepare_temperature_at_request(neighbour, msg_data["meeting_guid"], date_from)
                        await self.send(msg2)

    class ReceiveTemperatureAtInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                # print(msg)
                msg_data = json.loads(msg.body)
                guid = msg_data["request_guid"]
                self.agent.score_request_dict[guid]["temperatures"].append(msg_data["temperature"])
                if len(self.agent.score_request_dict[guid]["temperatures"]) == len(self.agent.neighbours):
                    sum_n = 0
                    for temp in self.agent.score_request_dict[guid]["temperatures"]:
                        sum_n = sum_n + temp
                    sum_n = sum_n / len(self.agent.neighbours)
                    temp = self.agent.personal_calendar.get_temperature_at(
                        self.agent.score_request_dict[guid]["date_from"])
                    temp = (temp + 0.1 * sum_n) / 1.1
                    msg2 = MeetingRoomAgent.prepare_meeting_score_inform(self.agent.central, guid, abs(
                        temp - self.agent.score_request_dict[guid]["temperature"]))
                    await self.send(msg2)

    class ReceiveTemperatureAtRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                # print(msg)
                msg_data = json.loads(msg.body)
                temp = self.agent.personal_calendar.get_temperature_at(str_to_time(msg_data["date"]))
                msg2 = MeetingRoomAgent.prepare_temperature_at_inform(msg.sender, msg_data["request_guid"], temp)
                await self.send(msg2)

    class ReceiveOutdoorTemperatureInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                self.agent.outdoor_temperature = msg_data["temperature"]

    async def setup(self):
        print(str(self.jid) + " Meeting room agent setup")

        temperature_at_request_template = Template()
        temperature_at_request_template.set_metadata('performative', 'request')
        temperature_at_request_template.set_metadata('type', 'temperature_at_request')
        self.add_behaviour(self.ReceiveTemperatureAtRequestBehaviour(), temperature_at_request_template)

        temperature_at_inform_template = Template()
        temperature_at_inform_template.set_metadata('performative', 'inform')
        temperature_at_inform_template.set_metadata('type', 'temperature_at_inform')
        self.add_behaviour(self.ReceiveTemperatureAtInformBehaviour(), temperature_at_inform_template)

        meeting_score_request_template = Template()
        meeting_score_request_template.set_metadata('performative', 'request')
        meeting_score_request_template.set_metadata('type', 'meeting_score_request')
        self.add_behaviour(self.ReceiveMeetingScoreRequestBehaviour(), meeting_score_request_template)

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

        datetime_inform_template = Template()
        datetime_inform_template.set_metadata('performative', 'inform')
        datetime_inform_template.set_metadata("type", "datetime_inform")
        datetimeBehaviour = self.ReceiveDatetimeInformBehaviour()
        self.add_behaviour(datetimeBehaviour, datetime_inform_template)

        self.add_behaviour(self.ReceiveNewMeetingInformBehaviour(), self.new_meeting_inform_template)

        outdoor_temperature_inform_template = Template()
        outdoor_temperature_inform_template.set_metadata('performative', 'inform')
        outdoor_temperature_inform_template.set_metadata('type', 'outdoor_temperature_inform')
        outdoor_temperature_inform_behaviour = self.ReceiveOutdoorTemperatureInformBehaviour()
        self.add_behaviour(outdoor_temperature_inform_behaviour, outdoor_temperature_inform_template)


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
