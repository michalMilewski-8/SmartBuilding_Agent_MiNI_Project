from datetime import datetime

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json
from agents.central_agent.CentralAgent import CentralAgent
from agents.private_room_agent.PrivateRoomAgent import PrivateRoomAgent
from agents.personal_agent.PersonalAgent import PersonalAgent
from agents.technical_agent.TechnicalAgent import TechnicalAgent
from agents.thermometer_agent.thermometer import Thermometer
import time
import sys



if __name__ == "__main__":
    personal1 = PersonalAgent("personal1@localhost", "personal")
    personal2 = PersonalAgent("personal2@localhost", "personal")
    personal3 = PersonalAgent("personal3@localhost", "personal")
    personal4 = PersonalAgent("personal4@localhost", "personal")

    room1 = PrivateRoomAgent("room1@localhost", "room")
    room2 = PrivateRoomAgent("room2@localhost", "room")
    room3 = PrivateRoomAgent("room3@localhost", "room")
    room4 = PrivateRoomAgent("room4@localhost", "room")

    personal1.set_personal_room("room1@localhost")
    personal2.set_personal_room("room2@localhost")
    personal3.set_personal_room("room3@localhost")
    personal4.set_personal_room("room4@localhost")

    room1.people = ["personal1@localhost"]
    room2.people = ["personal2@localhost"]
    room3.people = ["personal3@localhost"]
    room4.people = ["personal4@localhost"]

    personal1.start()
    personal2.start()
    personal3.start()
    personal4.start()
    room1.start()
    room2.start()
    room3.start()
    room4.start()

    time.sleep(5)

    personal1.set_preferred_temperature(20)
    personal2.set_preferred_temperature(19)
    personal3.set_preferred_temperature(25)
    personal4.set_preferred_temperature(23)	

    # wait until user interrupts with ctrl+C
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            break

    personal1.stop()
    personal2.stop()
    personal3.stop()
    personal4.stop()
    room1.stop()
    room2.stop()
    room3.stop()
    room4.stop()
