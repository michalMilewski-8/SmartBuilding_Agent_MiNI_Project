import json
import pandas as pd
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
from ..time_conversion import time_to_str, str_to_time

import os
cwd = os.getcwd()
print(cwd)
temp_data = pd.read_csv(
    'agents/thermometer_agent/weather2019warsaw.csv',
    parse_dates=['Local time in Warsaw / Okecie (airport)'],
    index_col='Local time in Warsaw / Okecie (airport)')  

class Thermometer(Agent):
    async def setup(self):
        print("Thermometer setup")
        template = Template()
        template.set_metadata('performative', 'request')
        template.set_metadata('type', 'outdoor_temperature')
        b = self.SendTemperature()
        self.add_behaviour(b)

    class SendTemperature(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout = 1)
            if(msg):
                date_dict = json.loads(msg.body)
                date = str_to_time(date_dict['date'])
                temp = self.agent.get_temperature(pd.Timestamp(date))
                temp_msg = msg.make_reply()
                temp_msg.body = json.dumps({'temperature': temp})
                temp_msg.set_metadata('performative', 'inform')
                temp_msg.set_metadata('type', 'outdoor_temperature_inform')
                await self.send(temp_msg)


    def get_temperature(self, date):       
        date = date.round('30min')
        date = pd.Timestamp(year=2019, month=date.month, day=date.day,
            hour=date.hour, minute=date.minute)
        return temp_data['T'][date]
