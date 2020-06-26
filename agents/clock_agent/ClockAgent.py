from datetime import datetime
from datetime import timedelta

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
from ..time_conversion import time_to_str, str_to_time

class ClockAgent(Agent):

    def __init__(self, jid, password, time_speed=60, time_step=5):
        super().__init__(jid, password)
        self.last_date_virtual = datetime.now()
        self.last_date_real = datetime.now()
        self.agents_jids = []
        self.time_step = time_step*60
        self.time_speed = time_speed

    async def setup(self):
        print('Clock setup')
        send_date_behaviour = self.SendDate(period=self.time_step/self.time_speed)
        self.add_behaviour(send_date_behaviour)

    class SendDate(PeriodicBehaviour):
        async def run(self): 
         #   real_time_difference = datetime.now() - self.agent.last_date_real
         #    self.agent.last_date_real = datetime.now()
         #   virtual_time_difference = real_time_difference * self.agent.time_speed
         #   virtual_date = self.agent.last_date_virtual + virtual_time_difference
            virtual_date = self.agent.last_date_virtual + timedelta(seconds = self.agent.time_step) # jeśli chcesz wrócić do starej wersji zakomentuj tą linie i odkomentuj te wyżej
            self.agent.last_date_virtual = virtual_date
            for agent in self.agent.agents_jids:
                #print(str(self.agent.jid) + " sending date to " + agent)
                msg = Message(to = agent)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("type", "datetime_inform")
                msg.body = json.dumps({'datetime': time_to_str(virtual_date)})
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
