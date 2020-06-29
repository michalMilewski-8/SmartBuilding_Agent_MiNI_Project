from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from datetime import datetime,timedelta
from ..energy import heat_balance, air_conditioner
from ..sb_calendar import Calendar
from ..time_conversion import time_to_str, str_to_time
import json
import time
import runtime_switches


class PrivateRoomAgent(Agent):

    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.personal_calendar = Calendar()
        self.score_request_dict = {}
        self.central = ""
        self.neighbours = {}
        self.people = []
        self.temperature = runtime_switches.boundary_down + (
                runtime_switches.boundary_up - runtime_switches.boundary_down) / 2
        self.preferred_temperature = 20
        self.preferred_temperatures = {}
        self.outdoor_agent = ""
        self.energy_agent = ""
        self.date = datetime.now()
        self.coming_at = {}
        self.default_day_start = 7
        self.end_of_day = 17
        self.ac_power = 0
        self.room_capacity = 200
        self.ac_performance = 1
        self.outdoor_wall = 20
        self.outdoor_temperature = self.temperature
        self.first_guy_coming_at = self.date.replace(hour=self.default_day_start, minute=0, second=0)
        self.light_const = 10000

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
    def prepare_temperature_at_inform(receivers, guid, temperature):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'temperature_at_inform')
        msg.body = json.dumps({'request-guid': guid, 'temperature': temperature})
        return msg

    class ReceiveRoomDataExchangeRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                temperature = msg_data["temperature"]
                self.agent.neighbours[str(msg.sender)]["temperature"] = temperature
                if runtime_switches.log_level >= 4:
                    print(str(self.agent.jid) + " received exchange request from " + str(msg.sender) + " with " + str(self.agent.neighbours[str(msg.sender)]["temperature"]))
                msg2 = PrivateRoomAgent.prepare_room_data_inform(self.agent.temperature, str(msg.sender))
                if runtime_switches.log_level >= 4:
                    print(str(self.agent.jid) + " sending exchange inform to " + str(msg.sender) + " with " + str(self.agent.temperature))
                await self.send(msg2)

    class ReceiveRoomDataInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                self.agent.neighbours[str(msg.sender)]["temperature"] = msg_data["temperature"]
                if runtime_switches.log_level >= 4:
                    print(str(self.agent.jid) + " received exchange inform from " + str(msg.sender) + " with " + str(self.agent.neighbours[str(msg.sender)]["temperature"]))

    class SendRoomDataExchangeRequestBehaviour(OneShotBehaviour):
        async def run(self):
            for neighbour in self.agent.neighbours:
                if neighbour < str(self.agent.jid):
                    msg = PrivateRoomAgent.prepare_room_data_exchange_request(self.agent.temperature, neighbour)
                    if runtime_switches.log_level >= 4:
                        print(str(self.agent.jid) + " sending exchange request to " + neighbour + " with " + str(self.agent.temperature))
                    await self.send(msg)

    class ReceiveDatetimeInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                new_time = str_to_time(msg_data['datetime'])
                last_time = self.agent.date
                if last_time.day != new_time.day:
                    self.agent.first_guy_coming_at = new_time.replace(hour=self.agent.default_day_start, minute=0, second=0)
                self.agent.date = new_time
                if runtime_switches.log_level >= 3:
                    print(str(self.agent.jid) + " current date: {}".format(self.agent.date))
                time_elapsed = new_time - last_time
                b = self.agent.SendEnergyUsageInformBehaviour()
                if runtime_switches.add_light_and_conditioning_const:
                    if runtime_switches.optimize_lightning:
                        if new_time > self.agent.first_guy_coming_at and new_time.hour < self.agent.end_of_day:
                            b.set_energy(abs(self.agent.ac_power * time_elapsed.seconds) + self.agent.light_const)
                        else:
                            b.set_energy(abs(self.agent.ac_power * time_elapsed.seconds))
                    else:
                        b.set_energy(abs(self.agent.ac_power * time_elapsed.seconds) + self.agent.light_const)
                else:
                    b.set_energy(abs(self.agent.ac_power * time_elapsed.seconds))
                self.agent.add_behaviour(b)

                if time_elapsed.seconds > 0:
                    energy_used = self.agent.ac_power * time_elapsed.seconds
                    heat_lost_per_second, heat_lost, temperature_lost = heat_balance(
                        time_elapsed, self.agent.temperature, self.agent.room_capacity,
                        self.agent.neighbours, self.agent.ac_power,
                        self.agent.outdoor_wall, self.agent.outdoor_temperature)
                    self.agent.temperature -= temperature_lost
                    if runtime_switches.log_level >= 1:
                        print(str(self.agent.jid) + " temp " + str(self.agent.temperature))
                    if (len(self.agent.people) > 0 and self.agent.date.hour < self.agent.end_of_day and self.agent.date.hour-1 >= self.agent.first_guy_coming_at.hour) or not runtime_switches.private_room_optimal_heating:
                        heat_needed = air_conditioner(self.agent.temperature,
                                                    self.agent.preferred_temperature, self.agent.room_capacity)
                    else:
                        if self.agent.temperature < runtime_switches.boundary_down:
                            heat_needed = air_conditioner(self.agent.temperature,
                                                          runtime_switches.boundary_down, self.agent.room_capacity)
                        elif self.agent.temperature > runtime_switches.boundary_up:
                            heat_needed = air_conditioner(self.agent.temperature,
                                                          runtime_switches.boundary_up, self.agent.room_capacity)
                        else:
                            heat_needed = 0
                    if self.agent.date < self.agent.first_guy_coming_at and runtime_switches.private_room_optimal_heating:
                        diff = self.agent.first_guy_coming_at - self.agent.date
                        if diff.seconds > 0:
                            self.agent.ac_power = heat_needed / diff.seconds / self.agent.ac_performance
                        else:
                            self.agent.ac_power = heat_needed / time_elapsed.seconds / self.agent.ac_performance
                    else:
                        self.agent.ac_power = heat_needed / time_elapsed.seconds / self.agent.ac_performance
                b2 = self.agent.SendRoomDataExchangeRequestBehaviour()
                self.agent.add_behaviour(b2)
                b3 = self.agent.SendOutdoorTemperatureRequestBehaviour()
                self.agent.add_behaviour(b3)

    class ReceiveJobLateInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                new_time = str_to_time(msg_data['arrival_datetime'])
                sender_jid = str(msg.sender)
                self.agent.coming_at[sender_jid] = new_time
                first_coming_at = new_time
                for agent_jid in self.agent.coming_at:
                    if self.agent.coming_at[agent_jid] < self.agent.first_guy_coming_at:
                        first_coming_at = self.agent.coming_at[agent_jid]
                self.agent.first_guy_coming_at = first_coming_at

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

    class ReceivePreferencesInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = (json.loads(msg.body))
                if "optimal_temperature" in msg_data:
                    if runtime_switches.log_level >= 2:
                        print("Preferred temperature: {}".format(msg_data.get("optimal_temperature")))
                    self.agent.preferred_temperatures[str(msg.sender)] = msg_data.get("optimal_temperature")
                    sum_n = 0
                    for agent_jid in self.agent.preferred_temperatures:
                        sum_n = sum_n + self.agent.preferred_temperatures[agent_jid]
                    self.agent.preferred_temperature = sum_n / len(self.agent.preferred_temperatures)
                    if runtime_switches.log_level >= 1:
                        print("Temperature set: {}".format(self.agent.preferred_temperature))

    class ReceiveTemperatureAtRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                temp = self.agent.personal_calendar.get_temperature_at(msg_data["date"])
                msg2 = PrivateRoomAgent.prepare_temperature_at_inform(msg.sender, msg_data["request_guid"],
                                                                      self.agent.pregferred_temperature)
                await self.send(msg2)

    class ReceiveOutdoorTemperatureInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                self.agent.outdoor_temperature = msg_data["temperature"]

    async def setup(self):
        if runtime_switches.log_level >= 0:
            print(str(self.jid) + " Private room agent setup")
        self.first_guy_coming_at = self.date.replace(hour=self.default_day_start, minute=0, second=0)

        datetime_inform_template = Template()
        datetime_inform_template.set_metadata('performative', 'inform')
        datetime_inform_template.set_metadata("type", "datetime_inform")
        datetimeBehaviour = self.ReceiveDatetimeInformBehaviour()
        self.add_behaviour(datetimeBehaviour, datetime_inform_template)

        preferences_inform_template = Template()
        preferences_inform_template.set_metadata('performative', 'inform')
        preferences_inform_template.set_metadata('type', 'preferences_inform')
        preferences_behaviour = self.ReceivePreferencesInformBehaviour()
        self.add_behaviour(preferences_behaviour, preferences_inform_template)

        temperature_at_request_template = Template()
        temperature_at_request_template.set_metadata('performative', 'request')
        temperature_at_request_template.set_metadata('type', 'temperature_at_request')
        receive_temperature_at_request_behaviour = self.ReceiveTemperatureAtRequestBehaviour()
        self.add_behaviour(receive_temperature_at_request_behaviour, temperature_at_request_template)

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

        job_late_inform_template = Template()
        job_late_inform_template.set_metadata('performative', 'inform')
        job_late_inform_template.set_metadata('type', 'job_late_inform')
        job_late_inform_behaviour = self.ReceiveJobLateInformBehaviour()
        self.add_behaviour(job_late_inform_behaviour, job_late_inform_template)

        outdoor_temperature_inform_template = Template()
        outdoor_temperature_inform_template.set_metadata('performative', 'inform')
        outdoor_temperature_inform_template.set_metadata('type', 'outdoor_temperature_inform')
        outdoor_temperature_inform_behaviour = self.ReceiveOutdoorTemperatureInformBehaviour()
        self.add_behaviour(outdoor_temperature_inform_behaviour, outdoor_temperature_inform_template)

    def add_personal_agent(self, personal_agent_jid):
        self.people.append(personal_agent_jid)
        self.coming_at[personal_agent_jid] = self.date.replace(hour=self.default_day_start, minute=0, second=0)
        self.first_guy_coming_at = self.date.replace(hour=self.default_day_start, minute=0, second=0)


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
