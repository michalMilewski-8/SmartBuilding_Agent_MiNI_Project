import json
import pandas as pd
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message

temp = pd.read_csv('EPWA.01.01.2019.31.12.2019.1.0.0.en.ansi.00000000.csv',
    parse_dates=['Local time in Warsaw / Okecie (airport)'])
print(temp.head())
print(type(temp['Local time in Warsaw / Okecie (airport)'][1]))
print(temp['Local time in Warsaw / Okecie (airport)'][1])

class Thermometer(Agent):
    def setup(self):        
        b = self.MyBehav()
        self.add_behaviour(b)

    class MyBehav(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            date_dict = json.loads(msg.body)
            date = date_dict['date']
            temp = Thermometer.get_temperature(pd.Timestamp(date))

            temp_msg = msg.make_reply()
            msg.body = json.dumps({'temperature': temp})
            msg.set_metadata('performative', 'inform')
            msg.set_metadata('type', 'outdoor_temperature_response')
            await self.send(temp_msg)



    @staticmethod
    def get_temperature(date):   
        temp_data = pd.read_csv(
            'EPWA.01.01.2019.31.12.2019.1.0.0.en.ansi.00000000.csv',
            parse_dates=['Local time in Warsaw / Okecie (airport)'],
            index_col='Local time in Warsaw / Okecie (airport)')     
        date = date.round('30min')
        date = pd.Timestamp(year=2019, month=date.month, day=date.day,
            hour=date.hour, minute=date.minute)
        return temp_data['T'][date]