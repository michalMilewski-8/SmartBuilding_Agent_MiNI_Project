import json
import pandas as pd
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template

import os
cwd = os.getcwd()
print(cwd)
temp_data = pd.read_csv(
    'agents/thermometer_agent/weather2019warsaw.csv',
    parse_dates=['Local time in Warsaw / Okecie (airport)'],
    index_col='Local time in Warsaw / Okecie (airport)')  

class Thermometer(Agent):
    async def setup(self):
        template = Template()
        template.set_metadata('performative', 'request')
        template.set_metadata('type', 'outdoor_temperature')
        b = self.SendTemperature()
        self.add_behaviour(b)

    class SendTemperature(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            date_dict = json.loads(msg.body)
            date = date_dict['date']
            temp = self.agent.get_temperature(pd.Timestamp(date))

            temp_msg = msg.make_reply()
            msg.body = json.dumps({'temperature': temp})
            msg.set_metadata('performative', 'inform')
            msg.set_metadata('type', 'outdoor_temperature_response')
            await self.send(temp_msg)


    def get_temperature(self, date):       
        date = date.round('30min')
        date = pd.Timestamp(year=2019, month=date.month, day=date.day,
            hour=date.hour, minute=date.minute)
        return temp_data['T'][date]
