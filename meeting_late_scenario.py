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
import time
import sys



if __name__ == "__main__":
    personal1 = PersonalAgent("personal1@localhost", "personal")
    personal2 = PersonalAgent("personal2@localhost", "personal")

    room1 = MeetingRoomAgent("room1@localhost", "room")
    room2 = MeetingRoomAgent("room2@localhost", "room")
    room3 = MeetingRoomAgent("room3@localhost", "room")
    room4 = MeetingRoomAgent("room4@localhost", "room")

    centralny = CentralAgent("central@localhost", "central")

    room1.central = "central@localhost"
    personal1.central = "central@localhost"
    personal2.central = "central@localhost"
    room2.central = "central@localhost"
    room3.central = "central@localhost"
    room4.central = "central@localhost"

    room1.neighbours = ["room2@localhost"]
    room2.neighbours = ["room1@localhost", "room3@localhost"]
    room3.neighbours = ["room2@localhost", "room4@localhost"]
    room4.neighbours = ["room3@localhost"]

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

    time.sleep(1)

    personal1.new_meeting_set(datetime(2020, 5, 22, 22, 00), datetime(2020, 5, 22, 23, 00), 23, [])
    time.sleep(5)
    guid = list(personal1.personal_calendar.get_events().keys())[0]
    personal1.meeting_late(datetime(2020, 5, 22, 22, 15), guid, True)
    time.sleep(5)
    personal1.meeting_late(datetime(2020, 5, 22, 22, 30), guid, False)
    

    # wait until user interrupts with ctrl+C
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            break

    centralny.stop()
    personal1.stop()
    personal2.stop()
    room1.stop()
    room2.stop()
    room3.stop()
    room4.stop()
