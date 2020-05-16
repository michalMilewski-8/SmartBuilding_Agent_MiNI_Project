from datetime import datetime
import json
import sys
sys.path.insert(1, 'agents')
from sb_calendar import Calendar
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from spade.template import Template

class ClockAgent(Agent):
    def setup(self):
        self.start_date_virtual = datetime.strptime(sys.argv[1], "%Y-%m-%d %H:%M")
        self.start_date_real = datetime.now()
        self.agents_jids = ["aaa@bbb"]
        send_date_behaviour = self.SendDate(period = 10)
        self.add_behaviour(send_date_behaviour)
        
    class SendDate(PeriodicBehaviour):
        async def run(self):
            for agent in self.agent.agents_jids:
                msg = Message(to = agent)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("type", "datetime_inform")
                real_time_difference = datetime.now() - self.agent.start_date_real
                virtual_time_difference = real_time_difference / 360
                virtual_date = self.agent.start_date_virtual + virtual_time_difference
                msg.body = json.dumps({'datetime': str(virtual_date)})
                await self.send(msg)

