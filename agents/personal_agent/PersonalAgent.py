from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from ..sb_calendar import Calendar

import json
import uuid
import time
import asyncio
from datetime import datetime

class PersonalAgent(Agent):

    personal_room_jid = ""
    preferred_temperature = 20
    personal_calendar = Calendar()

    @staticmethod
    def prepare_meet_request(self, guid, start_date, end_date, temperature, participants, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'meet')
        msg.body = json.dumps({'meeting_guid': guid, 'start_date': start_date, 'end_date': end_date,
                               'temperature': temperature, 'participants': participants})
        return msg

    @staticmethod
    def prepare_late_inform(self, arrival_datetime, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'late')
        msg.body = json.dumps({'arrival_datetime': arrival_datetime})
        return msg

    @staticmethod
    def prepare_preferences_inform(self, optimal_temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'preferences')
        msg.body = json.dumps({'optimal_temperature': optimal_temperature})
        return msg

    @staticmethod
    def prepare_accept_proposal(self, guid, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'accept_proposal')
        msg.set_metadata('type', 'accept_proposal')
        msg.body = json.dumps({'meeting_guid': guid})
        return msg

    @staticmethod
    def prepare_refuse_proposal(self, guid, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'refuse_proposal')
        msg.set_metadata('type', 'refuse_proposal')
        msg.body = json.dumps({'meeting_guid': guid})
        return msg
    
    meet_inform_template = Template()
    meet_inform_template.set_metadata('performative','inform')
    meet_inform_template.set_metadata('type','meet')

    new_meeting_inform_template = Template()
    new_meeting_inform_template.set_metadata('performative','inform')
    new_meeting_inform_template.set_metadata('type','new_meeting')

    late_confirm_template = Template()
    late_confirm_template.set_metadata('performative','confirm')
    late_confirm_template.set_metadata('type','late')

    move_meeting_propose_template = Template()
    move_meeting_propose_template.set_metadata('performative','propose')
    move_meeting_propose_template.set_metadata('type','move_meeting')

    move_meeting_inform_template = Template()
    move_meeting_inform_template.set_metadata('performative','inform')
    move_meeting_inform_template.set_metadata('type','move_meeting')

    class SendMeetRequestBehaviour(OneShotBehaviour):
        async def run(self):
            msg = PersonalAgent.prepare_meet_request(self, uuid.uuid4(), 'start_date', 'end_date', 20,
                                                     ['AA@AA', 'bb@bb'], 'central_agent')
            await self.send(msg)

    class SendLateInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = PersonalAgent.prepare_late_inform(self, 'arrival_date', 'central_agent')
            await self.send(msg)

    class ReceiveNewMeetingInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)
            agent.personal_calendar.add_event(msg_data.get('start_date'), msg_data.get('end_date'),
                                              msg_data.get('temperature'))

    class ReceiveDatetimeInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                self.agent.date = msg_data["datetime"]
                print(str(self.agent.jid) + " current date: {}".format(self.agent.date))

    class SendPreferencesInformBehaviour(OneShotBehaviour):
        async def run(self): 
            print('sending')
            msg = PersonalAgent.prepare_preferences_inform(self, agent.preferred_temperature, agent.personal_room_jid)
            await self.send(msg)

    class ReceiveMoveMeetingProposeBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)

    class ReceiveMoveMeetingInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)

    async def setup(self):
        print(str(self.jid) + " Personal agent setup")
        self.date = datetime.now()
        
        datetime_inform_template = Template()
        datetime_inform_template.set_metadata('performative','inform')
        datetime_inform_template.set_metadata("type","datetime_inform")
        datetimeBehaviour = self.ReceiveDatetimeInformBehaviour()
        self.add_behaviour(datetimeBehaviour, datetime_inform_template)

    def set_personal_room(self, personal_room_jid):
        self.personal_room_jid = personal_room_jid

    def set_preferred_temperature(self, preferred_temp):
        self.preferred_temperature = preferred_temp
        preferences = self.SendPreferencesInformBehaviour()
        self.add_behaviour(preferences)


if __name__ == "__main__":
    agent = PersonalAgent("personal@localhost", "personal")
    agent.start()

    # wait until user interrupts with ctrl+C
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    agent.stop()
