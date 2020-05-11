import datetime

AIR_COEFFICIENT = 721 # J / (kg * C)
AIR_DENSITY = 1.2 # kg / m**3

def heat_balance(time_elapsed, last_temperature, room_capacity, neighbors, ac_power):
    heat_lost_per_second = sum([surface * coef * (last_temperature - temp) for surface, coef, temp in neighbors]) - ac_power
    heat_lost = heat_lost_per_second * time_elapsed.seconds
    temperature_lost = heat_lost / (AIR_COEFFICIENT * room_capacity * AIR_DENSITY)
    return heat_lost_per_second, heat_lost, temperature_lost

def air_conditioner(last_temperature, needed_temperature, ac_performance, room_capacity):
    #ac_perf = ac_performance[0] if needed_temperature < last_temperature else ac_performance[1]
    heat_needed = AIR_COEFFICIENT * room_capacity * AIR_DENSITY * abs(needed_temperature - last_temperature) / ac_performance
    return heat_needed