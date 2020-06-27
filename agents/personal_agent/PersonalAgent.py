from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.behaviour import OneShotBehaviour
from spade.message import Message
from spade.template import Template
from datetime import datetime
from ..time_conversion import time_to_str, str_to_time
from ..sb_calendar import Calendar
import json
import uuid
import time
import runtime_switches


class PersonalAgent(Agent):

    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.preferred_temperature = 20
        self.personal_calendar = Calendar()
        self.central = ""
        self.room = ""  # id pokoju prywatnego
        self.date = datetime.now()

    @staticmethod
    def prepare_meet_request(self, guid, start_date, end_date, temperature, participants, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'request')
        msg.set_metadata('type', 'meet_request')
        msg.body = json.dumps(
            {'meeting_guid': guid, 'start_date': time_to_str(start_date), 'end_date': time_to_str(end_date),
             'temperature': temperature, 'participants': participants})
        return msg

    @staticmethod
    def prepare_late_inform(self, arrival_datetime, guid, force_move, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'late')
        msg.body = json.dumps({'arrival_datetime': time_to_str(arrival_datetime),
                               'meeting_guid': guid,
                               'force_move': force_move})
        return msg

    @staticmethod
    def prepare_preferences_inform(self, optimal_temperature, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'preferences_inform')
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

    @staticmethod
    def prepare_job_late_inform(self, date, receivers):
        msg = Message(to=receivers)
        msg.set_metadata('performative', 'inform')
        msg.set_metadata('type', 'job_late_inform')
        msg.body = json.dumps({'arrival_datetime': time_to_str(date)})
        return msg

    def new_meeting_set(self, start_date, end_date, temp, participants):
        new_meeting_behav = self.SendMeetRequestBehaviour()
        new_meeting_behav.set_meeting_details(start_date, end_date, temp, participants)
        self.add_behaviour(new_meeting_behav)

    def meeting_late(self, arrival_datetime, meeting_guid, force_move):
        late_inform_behav = self.SendLateInformBehaviour()
        late_inform_behav.set_details(arrival_datetime, meeting_guid, force_move)
        self.add_behaviour(late_inform_behav)

    def job_late(self, arrival_datetime):
        job_late_inform_behav = self.SendJobLateInformBehaviour()
        job_late_inform_behav.set_details(arrival_datetime)
        self.add_behaviour(job_late_inform_behav)

    def set_personal_room(self, personal_room_jid):
        self.room = personal_room_jid

    def set_preferred_temperature(self, preferred_temp):
        self.preferred_temperature = preferred_temp
        preferences = self.SendPreferencesInformBehaviour()
        self.add_behaviour(preferences)

    meet_inform_template = Template()
    meet_inform_template.set_metadata('performative', 'inform')
    meet_inform_template.set_metadata('type', 'meet_inform')

    meet_refuse_template = Template()
    meet_refuse_template.set_metadata('performative', 'refuse')
    meet_refuse_template.set_metadata('type', 'meet_refuse')

    new_meeting_inform_template = Template()
    new_meeting_inform_template.set_metadata('performative', 'inform')
    new_meeting_inform_template.set_metadata('type', 'new_meeting_inform')

    late_confirm_template = Template()
    late_confirm_template.set_metadata('performative', 'confirm')
    late_confirm_template.set_metadata('type', 'late')

    move_meeting_propose_template = Template()
    move_meeting_propose_template.set_metadata('performative', 'propose')
    move_meeting_propose_template.set_metadata('type', 'move_meeting')

    move_meeting_inform_template = Template()
    move_meeting_inform_template.set_metadata('performative', 'inform')
    move_meeting_inform_template.set_metadata('type', 'move_meeting')

    class SendMeetRequestBehaviour(OneShotBehaviour):

        def __init__(self):
            super().__init__()
            self.start_date = ''
            self.end_date = ''
            self.temp = 20
            self.participants = []

        def set_meeting_details(self, start_date, end_date, temp, participants):
            self.start_date = start_date
            self.end_date = end_date
            self.temp = temp
            self.participants = participants

        async def run(self):
            msg = PersonalAgent.prepare_meet_request(self, str(uuid.uuid4()), self.start_date, self.end_date, self.temp,
                                                     self.participants, self.agent.central)
            await self.send(msg)

    class SendLateInformBehaviour(OneShotBehaviour):
        def __init__(self):
            super().__init__()
            self.arrival_datetime = ''
            self.meeting_guid = ''
            self.force_move = False

        def set_details(self, arrival_datetime, meeting_guid, force_move):
            self.arrival_datetime = arrival_datetime
            self.meeting_guid = meeting_guid
            self.force_move = force_move

        async def run(self):
            msg = PersonalAgent.prepare_late_inform(self, self.arrival_datetime,
                                                    self.meeting_guid, self.force_move, self.agent.central)
            if runtime_switches.log_level >= 2:
                print(msg)
            await self.send(msg)

    class SendJobLateInformBehaviour(OneShotBehaviour):
        def __init__(self):
            super().__init__()
            self.arrival_datetime = ''

        def set_details(self, arrival_datetime):
            self.arrival_datetime = arrival_datetime

        async def run(self):
            msg = PersonalAgent.prepare_job_late_inform(self, self.arrival_datetime, self.agent.room)
            await self.send(msg)

    class ReceiveNewMeetingInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                if runtime_switches.log_level >= 2:
                    print(msg)
                msg_data = json.loads(msg.body)
                self.agent.personal_calendar.add_event(msg_data['meeting_guid'],
                                                       str_to_time(msg_data.get('start_date')),
                                                       str_to_time(msg_data.get('end_date')),
                                                       msg_data.get('temperature'))

    class ReceiveNewMeetingRefuseBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                if runtime_switches.log_level >= 2:
                    print(msg)
                msg_data = json.loads(msg.body)
                if runtime_switches.log_level >= 0:
                    print("meeting: " + msg_data['meeting_guid'] + " refused, no free rooms in time: " +
                      msg_data.get('start_date') + " to " + msg_data.get('end_date'))

    class ReceiveDatetimeInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                msg_data = json.loads(msg.body)
                self.agent.date = str_to_time(msg_data["datetime"])
                if runtime_switches.log_level >= 2:
                    print(str(self.agent.jid) + " current date: {}".format(self.agent.date))

    class SendPreferencesInformBehaviour(OneShotBehaviour):
        async def run(self):
            msg = PersonalAgent.prepare_preferences_inform(self, self.agent.preferred_temperature, self.agent.room)
            await self.send(msg)

    class ReceiveMoveMeetingProposeBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            msg_data = json.loads(msg.body)

    class ReceiveMoveMeetingInformBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=1)
            msg_data = json.loads(msg.body)

    async def setup(self):
        if runtime_switches.log_level >= 0:
            print(str(self.jid) + " Personal agent setup")

        datetime_inform_template = Template()
        datetime_inform_template.set_metadata('performative', 'inform')
        datetime_inform_template.set_metadata("type", "datetime_inform")
        self.add_behaviour(self.ReceiveDatetimeInformBehaviour(), datetime_inform_template)

        self.add_behaviour(self.ReceiveNewMeetingInformBehaviour(),
                           self.new_meeting_inform_template | self.meet_inform_template)

        self.add_behaviour(self.ReceiveNewMeetingRefuseBehaviour(),
                           self.meet_refuse_template)


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
