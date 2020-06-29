from datetime import datetime
from agents.private_room_agent.PrivateRoomAgent import PrivateRoomAgent
from agents.personal_agent.PersonalAgent import PersonalAgent
from agents.technical_agent.TechnicalAgent import TechnicalAgent
from agents.thermometer_agent.Thermometer import Thermometer
from agents.clock_agent.ClockAgent import ClockAgent
import time
import runtime_switches



if __name__ == "__main__":
    runtime_switches.private_room_optimal_heating = False
    runtime_switches.optimize_lightning = False

    start_date = datetime(2020,5,23,3,0)

    personal1 = PersonalAgent("personal1@localhost", "personal")
    personal2 = PersonalAgent("personal2@localhost", "personal")
    personal3 = PersonalAgent("personal3@localhost", "personal")
    personal4 = PersonalAgent("personal4@localhost", "personal")

    room1 = PrivateRoomAgent("room1@localhost", "room")
    room2 = PrivateRoomAgent("room2@localhost", "room")
    room3 = PrivateRoomAgent("room3@localhost", "room")
    room4 = PrivateRoomAgent("room4@localhost", "room")

    technical = TechnicalAgent("technical@localhost", "technical")
    thermometer = Thermometer("thermometer@localhost", "thermometer")

    clock = ClockAgent("clock@localhost", "clock")
    clock.agents_jids = ["room1@localhost", "room2@localhost", "room3@localhost", "room4@localhost",
                        "personal1@localhost", "personal2@localhost", "personal3@localhost", "personal4@localhost"]
    clock.last_date_virtual = start_date
    clock.time_speed = 1600
    clock.time_step = 30*60

    personal1.set_personal_room("room1@localhost")
    personal2.set_personal_room("room2@localhost")
    personal3.set_personal_room("room3@localhost")
    personal4.set_personal_room("room4@localhost")

    room1.add_personal_agent("personal1@localhost")
    room2.add_personal_agent("personal2@localhost")
    room3.add_personal_agent("personal3@localhost")
    room4.add_personal_agent("personal4@localhost")
    room1.energy_agent = "technical@localhost"
    room2.energy_agent = "technical@localhost"
    room3.energy_agent = "technical@localhost"
    room4.energy_agent = "technical@localhost"
    
    room1.date = start_date
    room2.date = start_date
    room3.date = start_date
    room4.date = start_date
    personal1.date = start_date
    personal2.date = start_date
    personal3.date = start_date
    personal4.date = start_date

    room1.temperature = 15
    room2.temperature = 15
    room3.temperature = 15
    room4.temperature = 20

    room1.outdoor_agent = 'thermometer@localhost'
    room2.outdoor_agent = 'thermometer@localhost'
    room3.outdoor_agent = 'thermometer@localhost'
    room4.outdoor_agent = 'thermometer@localhost'

    room1.neighbours = {"room2@localhost": {"wall_size": 20, "temperature": room2.temperature}}
    room2.neighbours = {"room1@localhost": {"wall_size": 20, "temperature": room1.temperature}, "room3@localhost": {"wall_size": 30, "temperature": room3.temperature}}
    room3.neighbours = {"room2@localhost": {"wall_size": 30, "temperature": room2.temperature}, "room4@localhost": {"wall_size": 20, "temperature": room4.temperature}}
    room4.neighbours = {"room3@localhost": {"wall_size": 20, "temperature": room3.temperature}}

    personal1.start()
    personal2.start()
    personal3.start()
    personal4.start()
    room1.start()
    room2.start()
    room3.start()
    room4.start()
    technical.start()
    thermometer.start()

    time.sleep(5) #czekanie na uruchomienie sie wszystkich agentow wyzej

    clock.start()
    personal1.set_preferred_temperature(20)
    personal2.set_preferred_temperature(19)
    personal3.set_preferred_temperature(25)
    personal4.set_preferred_temperature(23)	

    time.sleep(2)

    personal1.job_late(datetime(2020,5,23,10,15))

    # wait until user interrupts with ctrl+C
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            break

    personal1.stop()
    personal2.stop()
    personal3.stop()
    personal4.stop()
    room1.stop()
    room2.stop()
    room3.stop()
    room4.stop()
    clock.stop()
    technical.stop()
    thermometer.stop()
