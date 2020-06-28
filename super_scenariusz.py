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
    parser.add_argument("--job_late_prob", "-j", help="probability to be late in job")
    parser.add_argument("--meeting_late_prob", "-b", help="probability to be late on meeting")
    parser.add_argument("--turn_off_optimalizations", "-t", help="turning off optimalizations", action="store_true")
    parser.add_argument("--log", "-l", help="set log level")
    parser.add_argument("--meeting_kwant",  help="set meeting timne kwant")
    parser.add_argument("--min_meeting_kwants",  help="set meeting minimal time kwants")
    parser.add_argument("--max_meeting_kwants",  help="set meeting maximal time kwants")
    parser.add_argument("--preferred_temp_private_min",  help="set minimal private room temerature")
    parser.add_argument("--preferred_temp_private_max",  help="set maximal private room temerature")
    parser.add_argument("--job_late_min",  help="set minimal job late hour")
    parser.add_argument("--job_late_max",  help="set maximal job late hour")
    parser.add_argument("--meeting_temp_min",  help="set minimal meeting temerature")
    parser.add_argument("--meeting_temp_max",  help="set maximal meeting temerature")
    parser.add_argument("--personal_wall_size",  help="set personal room wall size")
    parser.add_argument("--time_speed",  help="set time speed")
    parser.add_argument("--time_kwant",  help="set time kwant")
    parser.add_argument("--meeting_wall_size",  help="set meeting room wall size")
    parser.add_argument("--seed",  help="set random seed")

    random.seed(14)
    meeting_kwant = 15  # ile minut ma kwant spotkania
    min_meeting_kwants = 1  # ile minimalnie może trwać kwantów spotkanie
    max_meeting_kwants = 16  # ile maksymalnie może trwać kwantów spotkanie
    start_date = datetime(2020, 1, 1, 0, 0)
    preferred_temp_private_min = 20
    preferred_temp_private_max = 26
    job_late_min = 8
    job_late_max = 12
    job_late_prob = 70
    meeting_late_prob = 70
    meeting_temp_min = 16
    meeting_temp_max = 30
    personal_wall_size = 30
    time_speed = 200
    time_kwant = 15
    meeting_wall_size = 30
    number_of_people = 20
    number_of_meetings = 40
    number_of_simulated_days = 10
    number_of_meeting_rooms = 5
    cur_date = start_date


    args = parser.parse_args()

    if args.people:
        number_of_people = int(args.people)
    if args.rooms:
        number_of_meeting_rooms = int(args.rooms)
    if args.meetings:
        number_of_meetings = int(args.meetings)
    if args.days:
        number_of_simulated_days = int(args.days)
    if args.job_late_prob:
        job_late_prob = int(args.job_late_prob)
    if args.meeting_late_prob:
        meeting_late_prob = int(args.meeting_late_prob)
    if args.meeting_kwant:
        meeting_kwant = int(args.meeting_kwant)
    if args.min_meeting_kwants:
        min_meeting_kwants = int(args.min_meeting_kwants)
    if args.max_meeting_kwants:
        max_meeting_kwants = int(args.max_meeting_kwants)
    if args.preferred_temp_private_min:
        preferred_temp_private_min = int(args.preferred_temp_private_min)
    if args.preferred_temp_private_max:
        preferred_temp_private_max = int(args.preferred_temp_private_max)
    if args.job_late_min:
        job_late_min = int(args.job_late_min)
    if args.job_late_max:
        job_late_max = int(args.job_late_max)
    if args.meeting_temp_min:
        meeting_temp_min = int(args.meeting_temp_min)
    if args.meeting_temp_max:
        meeting_temp_max = int(args.meeting_temp_max)
    if args.personal_wall_size:
        personal_wall_size = int(args.personal_wall_size)
    if args.time_speed:
        time_speed = int(args.time_speed)
    if args.time_kwant:
        time_kwant = int(args.time_kwant)
    if args.meeting_wall_size:
        meeting_wall_size = int(args.meeting_wall_size)
    if args.seed:
        random.seed(int(args.seed))
    if args.log:
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
    print("czas trwania symulacji: ", lates_meeting_time)
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
                                                     meeting_room_agents[(i - 1) % number_of_meeting_rooms].temperature},
                                             str(meeting_room_agents[(i + 1) % number_of_meeting_rooms].jid):
                                                 {"wall_size": meeting_wall_size, "temperature":
                                                     meeting_room_agents[(i + 1) % number_of_meeting_rooms].temperature}}

    central.start()
    technical.start()
    thermometer.start()

    for i in range(0, number_of_people):
        personal_agents[i].start()
        personal_room_agents[i].start()

    for i in range(0, number_of_meeting_rooms):
        meeting_room_agents[i].start()

    time.sleep(5)

    for i in range(0, number_of_people):
        personal_agents[i].set_preferred_temperature(random.randint(preferred_temp_private_min, preferred_temp_private_max))

    for i in range(0, number_of_meetings):
        meeting_len = timedelta(minutes=meeting_kwant * random.randint(min_meeting_kwants, max_meeting_kwants))
        hmm = timedelta(minutes=random.randint(7*60, 18*60), days=random.randint(0, lates_meeting_time.days))
        meeting_start = start_date + hmm
        personal_agents[i % number_of_people].new_meeting_set(meeting_start, meeting_start + meeting_len,
                                                              random.randint(meeting_temp_min, meeting_temp_max), [])
        if random.random() <= meeting_late_prob/100:
            if hasattr(personal_agents[i % number_of_people], 'last_guid'):
                personal_agents[i % number_of_people].meeting_late(meeting_start + meeting_len / 2, 
                                                                personal_agents[i % number_of_people].last_guid,
                                                                True if random.random() < 0.5  else False)

    time.sleep(5)
    clock.start()

    # wait until user interrupts with ctrl+C
    while True:
        try:
            new_date = clock.last_date_virtual
            if new_date.day != cur_date.day:
                for i in range(0, number_of_people):
                    if random.random() <= job_late_prob/100:
                        personal_agents[i].job_late(new_date.replace(hour = random.randint(job_late_min, job_late_max)))
            cur_date = new_date
            time.sleep(2)
            if clock.last_date_virtual >= start_date + lates_meeting_time:
                break
        except KeyboardInterrupt:
            break

    clock.stop()

    for i in range(0, number_of_people):
        personal_agents[i].stop()
        personal_room_agents[i].stop()

    for i in range(0, number_of_meeting_rooms):
        meeting_room_agents[i].stop()

    central.stop()
    technical.stop()
    thermometer.stop()

    print("Power used till ", clock.last_date_virtual, " is ", technical.get_power())

