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
from meeting_room_agent.MeetingRoomAgent import MeetingRoomAgent
from private_room_agent.PrivateRoomAgent import PrivateRoomAgent

meeting_room_agent1 = MeetingRoomAgent("meeting_room1@localhost", "meeting_room1")
meeting_room_agent1.temperature = 19
meeting_room_agent1.temperatures = {
    "meeting_room2@localhost": 0,
    "private_room1@localhost": 0,
    "private_room2@localhost": 0
}
meeting_room_agent1.neighbours = ["private_room1@localhost", "private_room2@localhost", "meeting_room2@localhost"]
meeting_room_agent1.start()

meeting_room_agent2 = MeetingRoomAgent("meeting_room2@localhost", "meeting_room2")
meeting_room_agent2.temperature = 110
meeting_room_agent2.temperatures = {
    "meeting_room1@localhost": 0,
    "private_room1@localhost": 0,
    "private_room2@localhost": 0
}
meeting_room_agent2.neighbours = ["private_room1@localhost", "private_room2@localhost", "meeting_room1@localhost"]
meeting_room_agent2.start()

private_room_agent1 = PrivateRoomAgent("private_room1@localhost", "private_room1")
private_room_agent1.temperature = 23
private_room_agent1.temperatures = {
    "meeting_room2@localhost": 0,
    "meeting_room1@localhost": 0,
    "private_room2@localhost": 0
}
private_room_agent1.neighbours = ["meeting_room1@localhost", "private_room2@localhost", "meeting_room2@localhost"]
private_room_agent1.start()

private_room_agent2 = PrivateRoomAgent("private_room2@localhost", "private_room2")
private_room_agent2.temperature = 231
private_room_agent2.temperatures = {
    "meeting_room2@localhost": 0,
    "private_room1@localhost": 0,
    "meeting_room1@localhost": 0
}
private_room_agent2.neighbours = ["private_room1@localhost", "meeting_room1@localhost", "meeting_room2@localhost"]
private_room_agent2.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break
private_room_agent1.stop()
meeting_room_agent1.stop()
private_room_agent2.stop()
meeting_room_agent2.stop()