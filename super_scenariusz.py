from datetime import datetime, timedelta
from agents.central_agent.CentralAgent import CentralAgent
from agents.meeting_room_agent.MeetingRoomAgent import MeetingRoomAgent
from agents.personal_agent.PersonalAgent import PersonalAgent
from agents.technical_agent.TechnicalAgent import TechnicalAgent
from agents.thermometer_agent.Thermometer import Thermometer
from agents.clock_agent.ClockAgent import ClockAgent
from agents.private_room_agent.PrivateRoomAgent import PrivateRoomAgent
import time
import random
import argparse
import runtime_switches

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--people", "-p", help="set number of people")
    parser.add_argument("--rooms", "-r", help="set number of meeting rooms")
    parser.add_argument("--meetings", "-m", help="set number of meetings to schedule")
    parser.add_argument("--days", "-d", help="set number of days to simulate")
    parser.add_argument("--turn_off_optimalizations", "-t", help="turning off optimalizations", action="store_true")
    parser.add_argument("--log", "-l", help="set log level")

    random.seed(14)
    meeting_kwant = 15  # ile minut ma kwant spotkania
    min_meeting_kwants = 1  # ile minimalnie może trwać kwantów spotkanie
    max_meeting_kwants = 16  # ile maksymalnie może trwać kwantów spotkanie
    start_date = datetime(2020, 1, 1, 0, 0)
    preferred_temp_private_min = 20
    preferred_temp_private_max = 26
    meeting_temp_min = 16
    meeting_temp_max = 30
    personal_wall_size = 30
    time_speed = 600
    time_kwant = 15
    meeting_wall_size = 30
    number_of_people = 10
    number_of_meetings = 80
    number_of_simulated_days = 1
    number_of_meeting_rooms = 10

    args = parser.parse_args()

    if args.people:
        number_of_people = int(args.people)
    if args.rooms:
        number_of_meeting_rooms = int(args.rooms)
    if args.meetings:
        number_of_meetings = int(args.meetings)
    if args.days:
        number_of_simulated_days = int(args.days)
    if args.log:
        print(args.log)
        runtime_switches.log_level = int(args.log)
    if args.turn_off_optimalizations:
        runtime_switches.is_best_room_selected_for_meeting = False
        runtime_switches.is_temerature_modulated_to_best_one = False
        runtime_switches.optimize_lightning = False
        runtime_switches.private_room_optimal_heating = False


    technical_jid = "technical@localhost"
    thermometer_jid = "thermometer@localhost"
    clock_jid = "clock@localhost"
    central_jid = "central@localhost"
    password = "koronalia"

    technical = TechnicalAgent(technical_jid, "technical")
    thermometer = Thermometer(thermometer_jid, "thermometer")
    clock = ClockAgent(clock_jid, "clock", time_speed, time_kwant)
    central = CentralAgent(central_jid, "room")
    clock.last_date_virtual = start_date

    jid_suffix = '@localhost'
    meeting_room_jid_prefix = 'meeting_room'
    personal_room_jid_prefix = 'personal_room'
    personal_agent_jid_prefix = 'personal_agent'

    personal_agents = [None] * number_of_people
    personal_room_agents = [None] * number_of_people
    meeting_room_agents = [None] * number_of_meeting_rooms

    lates_meeting_time = timedelta(days=number_of_simulated_days)
    print("spotkanie zaczyna się o: ", lates_meeting_time)
    for i in range(0, number_of_people):
        personal_agents[i] = PersonalAgent(personal_agent_jid_prefix + str(i) + jid_suffix, password)
        personal_agents[i].date = start_date
        personal_agents[i].central = str(central_jid)
        clock.agents_jids.append(str(personal_agents[i].jid))

        personal_room_agents[i] = PrivateRoomAgent(personal_room_jid_prefix + str(i) + jid_suffix, password)
        personal_room_agents[i].date = start_date
        personal_room_agents[i].add_personal_agent(str(personal_agents[i].jid))
        personal_room_agents[i].energy_agent = technical_jid
        personal_room_agents[i].outdoor_agent = thermometer_jid
        clock.agents_jids.append(str(personal_room_agents[i].jid))

        personal_agents[i].set_personal_room(str(personal_room_agents[i].jid))

    for i in range(0, number_of_people):
        personal_room_agents[i].neighbours = {str(personal_room_agents[(i - 1) % number_of_people].jid):
                                                  {"wall_size": personal_wall_size, "temperature":
                                                      personal_room_agents[(i - 1) % number_of_people].temperature},
                                              str(personal_room_agents[(i + 1) % number_of_people].jid):
                                                  {"wall_size": personal_wall_size, "temperature":
                                                      personal_room_agents[(i + 1) % number_of_people].temperature}}

    for i in range(0, number_of_meeting_rooms):
        meeting_room_agents[i] = MeetingRoomAgent(meeting_room_jid_prefix + str(i) + jid_suffix, password)
        meeting_room_agents[i].date = start_date
        meeting_room_agents[i].central = central_jid
        meeting_room_agents[i].energy_agent = technical_jid
        meeting_room_agents[i].outdoor_agent = thermometer_jid
        central.add_meeting_room(str(meeting_room_agents[i].jid))
        clock.agents_jids.append(str(meeting_room_agents[i].jid))

    for i in range(0, number_of_meeting_rooms):
        meeting_room_agents[i].neighbours = {str(meeting_room_agents[(i - 1) % number_of_meeting_rooms].jid):
                                                 {"wall_size": meeting_wall_size, "temperature":
                                                     personal_room_agents[(i - 1) % number_of_people].temperature},
                                             str(meeting_room_agents[(i + 1) % number_of_meeting_rooms].jid):
                                                 {"wall_size": meeting_wall_size, "temperature":
                                                     personal_room_agents[(i + 1) % number_of_people].temperature}}

    central.start()
    technical.start()
    thermometer.start()

    processes = [None]*(number_of_people+number_of_people+number_of_meeting_rooms)

    for i in range(0, number_of_people):
        personal_agents[i].start()
        personal_room_agents[i].start()

    for i in range(0, number_of_meeting_rooms):
        meeting_room_agents[i].start()

    time.sleep(1)

    for i in range(0, number_of_people):
        personal_agents[i].set_preferred_temperature(random.randint(preferred_temp_private_min, preferred_temp_private_max))

    for i in range(0, number_of_meetings):
        meeting_len = timedelta(minutes=meeting_kwant * random.randint(min_meeting_kwants, max_meeting_kwants))
        hmm = timedelta(minutes=random.randint(7*60, 18*60), days=random.randint(0, lates_meeting_time.days))
        meeting_start = start_date + hmm
        personal_agents[i % number_of_people].new_meeting_set(meeting_start, meeting_start + meeting_len,
                                                              random.randint(meeting_temp_min, meeting_temp_max), [])

    time.sleep(5)
    clock.start()

    # wait until user interrupts with ctrl+C
    while True:
        time.sleep(1)
        if clock.last_date_virtual >= start_date + lates_meeting_time:
            break

    for i in range(0, number_of_people):
        personal_agents[i].stop()
        personal_room_agents[i].stop()

    for i in range(0, number_of_meeting_rooms):
        meeting_room_agents[i].stop()

    central.stop()
    technical.stop()
    thermometer.stop()
    clock.stop()

    print("Power used till ", clock.last_date_virtual, " is ", technical.get_power())

