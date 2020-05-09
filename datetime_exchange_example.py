from datetime import datetime
import json
import sys
import time
sys.path.insert(1, 'agents')
from sb_calendar import Calendar
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from spade.template import Template
from clock_agent.clock_agent import ClockAgent
from meeting_room_agent.MeetingRoomAgent import MeetingRoomAgent
from private_room_agent.PrivateRoomAgent import PrivateRoomAgent
from personal_agent.PersonalAgent import PersonalAgent
from central_agent.CentralAgent import CentralAgent

meeting_room_agent = MeetingRoomAgent("meeting_room@localhost", "meeting_room")
meeting_room_agent.start()

private_room_agent = MeetingRoomAgent("private_room@localhost", "private_room")
private_room_agent.start()

personal_agent = MeetingRoomAgent("personal@localhost", "personal")
personal_agent.start()

central_agent = MeetingRoomAgent("central@localhost", "central")
central_agent.start()

clock_agent = ClockAgent("clock@localhost", "clock")
clock_agent.agents_jids = ["meeting_room@localhost", "private_room@localhost", "personal@localhost", "central@localhost"]
clock_agent.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break
clock_agent.stop()
meeting_room_agent.stop()
private_room_agent.stop()
central_agent.stop()
personal_agent.stop()
