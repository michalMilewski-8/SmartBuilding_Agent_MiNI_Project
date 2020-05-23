import datetime

AIR_COEFFICIENT = 721 # J / (kg * C)
AIR_DENSITY = 1.2 # kg / m**3
WALL_COEFFICIENT = 0.1

def heat_balance(time_elapsed, last_temperature, room_capacity, neighbours, ac_power):
    heat_lost_per_second = 0 
    for neighbour in neighbours:
        surface = neighbours[neighbour]["wall_size"]
        temp = neighbours[neighbour]["temperature"]
        heat_lost_per_second += WALL_COEFFICIENT * surface * (last_temperature - temp)
    heat_lost_per_second -= ac_power
    heat_lost = heat_lost_per_second * time_elapsed.seconds
    temperature_lost = heat_lost / (AIR_COEFFICIENT * room_capacity * AIR_DENSITY)
    return heat_lost_per_second, heat_lost, temperature_lost

def air_conditioner(last_temperature, needed_temperature, room_capacity):
    heat_needed = AIR_COEFFICIENT * room_capacity * AIR_DENSITY * (needed_temperature - last_temperature)
    return heat_needed