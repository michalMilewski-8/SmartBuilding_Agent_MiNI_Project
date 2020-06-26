from datetime import datetime

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json
from agents.central_agent.CentralAgent import CentralAgent
from agents.meeting_room_agent.MeetingRoomAgent import MeetingRoomAgent
from agents.personal_agent.PersonalAgent import PersonalAgent
from agents.technical_agent.TechnicalAgent import TechnicalAgent
from agents.thermometer_agent.Thermometer import Thermometer
from agents.clock_agent.ClockAgent import ClockAgent
import time
import sys
import runtime_switches

if __name__ == "__main__":

    start_date = datetime(2021, 5, 21, 9, 0)

    technical = TechnicalAgent("technical@localhost", "technical")
    thermometer = Thermometer("thermometer@localhost", "thermometer")

    clock = ClockAgent("clock@localhost", "clock")
    clock.agents_jids = ["room1@localhost", "room2@localhost", "room3@localhost", "room4@localhost",
                         "personal1@localhost", "personal2@localhost"]
    clock.last_date_virtual = start_date
    clock.time_speed = 400

    personal1 = PersonalAgent("personal1@localhost", "personal")
    personal2 = PersonalAgent("personal2@localhost", "personal")

    room1 = MeetingRoomAgent("room1@localhost", "room")
    room2 = MeetingRoomAgent("room2@localhost", "room")
    room3 = MeetingRoomAgent("room3@localhost", "room")
    room4 = MeetingRoomAgent("room4@localhost", "room")

    centralny = CentralAgent("central@localhost", "room")

    room1.central = "central@localhost"
    personal1.central = "central@localhost"
    personal2.central = "central@localhost"
    room2.central = "central@localhost"
    room3.central = "central@localhost"
    room4.central = "central@localhost"

    room1.energy_agent = "technical@localhost"
    room2.energy_agent = "technical@localhost"
    room3.energy_agent = "technical@localhost"
    room4.energy_agent = "technical@localhost"

    room1.outdoor_agent = 'thermometer@localhost'
    room2.outdoor_agent = 'thermometer@localhost'
    room3.outdoor_agent = 'thermometer@localhost'
    room4.outdoor_agent = 'thermometer@localhost'

    room1.date = start_date
    room2.date = start_date
    room3.date = start_date
    room4.date = start_date
    personal1.date = start_date
    personal2.date = start_date

    room1.temperature = runtime_switches.boundary_down + (
                runtime_switches.boundary_up - runtime_switches.boundary_down) / 2
    room2.temperature = runtime_switches.boundary_down + (
                runtime_switches.boundary_up - runtime_switches.boundary_down) / 2
    room3.temperature = runtime_switches.boundary_down + (
                runtime_switches.boundary_up - runtime_switches.boundary_down) / 2
    room4.temperature = runtime_switches.boundary_down + (
                runtime_switches.boundary_up - runtime_switches.boundary_down) / 2

    room1.neighbours = {"room2@localhost": {"wall_size": 20, "temperature": room2.temperature}}
    room2.neighbours = {"room1@localhost": {"wall_size": 20, "temperature": room1.temperature},
                        "room3@localhost": {"wall_size": 30, "temperature": room3.temperature}}
    room3.neighbours = {"room2@localhost": {"wall_size": 30, "temperature": room2.temperature},
                        "room4@localhost": {"wall_size": 20, "temperature": room4.temperature}}
    room4.neighbours = {"room3@localhost": {"wall_size": 20, "temperature": room3.temperature}}

    centralny.add_meeting_room("room2@localhost")
    centralny.add_meeting_room("room1@localhost")
    centralny.add_meeting_room("room3@localhost")
    centralny.add_meeting_room("room4@localhost")

    centralny.start()
    personal1.start()
    personal2.start()
    room1.start()
    room2.start()
    room3.start()
    room4.start()
    technical.start()
    thermometer.start()

    time.sleep(1)
    clock.start()
    personal1.new_meeting_set(datetime(2021, 5, 21, 10, 00), datetime(2021, 5, 21, 11, 00), 36, [])
    personal2.new_meeting_set(datetime(2021, 5, 21, 10, 00), datetime(2021, 5, 21, 11, 00), 20, [])
    personal1.new_meeting_set(datetime(2021, 5, 21, 11, 1), datetime(2021, 5, 21, 16, 00), 30, [])
    personal2.new_meeting_set(datetime(2021, 5, 21, 11, 1), datetime(2021, 5, 21, 16, 00), 16, [])
    personal1.new_meeting_set(datetime(2021, 5, 21, 16, 1), datetime(2021, 5, 21, 18, 00), 30, [])

    # wait until user interrupts with ctrl+C
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    centralny.stop()
    personal1.stop()
    personal2.stop()
    room1.stop()
    room2.stop()
    room3.stop()
    room4.stop()
