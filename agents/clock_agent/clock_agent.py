from datetime import datetime
import json
import sys
import time
#sys.path.insert(1, 'agents')
#from sb_calendar import Calendar
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
import asyncio

class ClockAgent(Agent):

    async def setup(self):
        self.start_date_virtual = datetime.now()
        self.start_date_real = datetime.now()
        print(self.agents_jids)
        send_date_behaviour = self.SendDate(period = 2)
        self.add_behaviour(send_date_behaviour)

    class SendDate(PeriodicBehaviour):
        async def run(self): 
            for agent in self.agent.agents_jids:
                print("sending date to " + agent)
                msg = Message(to = agent)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("type", "datetime_inform")
                real_time_difference = datetime.now() - self.agent.start_date_real
                virtual_time_difference = real_time_difference / 360
                virtual_date = self.agent.start_date_virtual + virtual_time_difference
                msg.body = json.dumps({'datetime': str(virtual_date)})
                await self.send(msg)

if __name__ == "__main__":
    agent = ClockAgent("clock@localhost", "clock")
    agent.agents_jids=["aa"]
    agent.start()

    # wait until user interrupts with ctrl+C
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    agent.stop()
