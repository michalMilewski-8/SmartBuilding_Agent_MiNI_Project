from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template
from spade import quit_spade
import json
import uuid
import time


class PersonalAgent(Agent):

    @staticmethod
    def prepare_meet_request(self, guid, start_date, end_date, temperature, participants ,receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'meet')
        msg.body = json.dumps({'meeting_guid': guid, 'start_date': date, 'end_date': end_date, 'temperature': temperature, 'participants':participants})
        return msg

    @staticmethod
    def prepare_late_inform(self, arrival_datetime ,receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'late')
        msg.body = json.dumps({'arrival_datetime': arrival_datetime})
        return msg

    @staticmethod
    def prepare_preferences_inform(self, optimal_temperature ,receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'preferences')
        msg.body = json.dumps({'optimal_temperature': optimal_temperature})
        return msg

    @staticmethod
    def prepare_accept_proposal(self, guid ,receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'accept_proposal')
        msg.set_metadata('type', 'accept_proposal')
        msg.body = json.dumps({'meeting_guid': guid})
        return msg

    @staticmethod
    def prepare_refuse_proposal(self, guid ,receivers):
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

    datetime_inform_template = Template()
    datetime_inform_template.set_metadata('performative','inform')
    datetime_inform_template.set_metadata('type','datetime')

    move_meeting_propose_template = Template()
    move_meeting_propose_template.set_metadata('performative','propose')
    move_meeting_propose_template.set_metadata('type','move_meeting')

    move_meeting_inform_template = Template()
    move_meeting_inform_template.set_metadata('performative','inform')
    move_meeting_inform_template.set_metadata('type','move_meeting')

    class SendMeetRequestBehaviour(CyclicBehaviour):
        async def run(self):
            msg = PersonalAgent.prepare_meet_request(self, uuid.uuid4(), 'start_date','end_date',20,['AA@AA', 'bb@bb'],'central_agent')
            await self.send(msg)
            #tu czekanie na template meet_inform

    class SendLateInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = PersonalAgent.prepare_late_inform(self, 'arrival_date', 'central_agent')
            await self.send(msg)
            #tu czekanie na template late_confirm

    class ReceiveNewMeetingInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)

    class ReceiveDatetimeInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)

    class SendPreferencesInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = PersonalAgent.prepare_preferences_inform(self, 'arrival_date', 'private_room_agent')
            await self.send(msg)

    class ReceiveMoveMeetingProposeBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)
            # wyslane accept lub refuse

    class ReceiveMoveMeetingInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()
            msg_data = json.loads(msg.body)

    async def setup(self):
        print("Personal agent setup")
        # sending = self.SendMeetRequestBehaviour()
        # self.add_behaviour(sending)
        # late_inform = self.SendLateInformBehaviour()
        # self.add_behaviour(late_inform)
        # new_meeting = self.ReceiveNewMeetingInformBehaviour()
        # self.add_behaviour(new_meeting,new_meeting_inform_template)
        # datetime_inform = self.ReceiveDatetimeInformBehaviour()
        # self.add_behaviour(datetime_inform,datetime_inform_template)
        # preferences = self.SendPreferencesInformBehaviour()
        # self.add_behaviour(preferences)
        # move_meeting_propose = self.ReceiveMoveMeetingProposeBehaviour()
        # self.add_behaviour(move_meeting_propose,move_meeting_propose_template)
        # move_meeting_inform = self.ReceiveMoveMeetingInformBehaviour()
        # self.add_behaviour(move_meeting_inform,move_meeting_inform_template)


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
