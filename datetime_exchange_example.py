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

clock_agent = ClockAgent("clock@localhost", "clock")
clock_agent.agents_jids = ["gunwo"]
clock_agent.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break
clock_agent.stop()
