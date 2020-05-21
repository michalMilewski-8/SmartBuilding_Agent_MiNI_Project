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
from agents.thermometer_agent.thermometer import Thermometer
import time
import sys



if __name__ == "__main__":
    agent = PersonalAgent("personal@localhost", "personal")

    # wait until user interrupts with ctrl+C
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
