# wiadomość od kalendarza do pokoju
new_meeting = {
    "date": "23-01-2020 12:23",
    "temperature": 30,
    "organizer_jid": "aaa@lll"
}

# wiadomość od kalendarza do agenta technicznego
power_data_request = {}

# wiadomość od technicznego do agenta kalendarza
power_data_response = {
    "power":1234
}

# wiadomość od pokoju do pokoju
room_data_exchange_request = {
    "temperature": 20,
}

# wiadomość od pokoju do pokoju (uznalem ze dodam zeby bylo wiadomo na co to jest odpowiedz)
room_data_exchange_response = {
    "temperature": 20,
}

# wiadomość od pokoju do pokoju
room_data_response = {
    "temperature": 20,
}

# wiadomość od pokoju do pokoju
room_data_request = {}

# wiadomość od pokoju/centranego do zewnetrzego 
outdoor_temperature_request = {
    "date": "23-01-2020 12:23"
}

# wiadomość od zewnetrzego do pokoju/centranego
outdoor_temperature_response = {
    "temperature": 20
}

# wiadomość od personalnego do centranego
meet_request = {
    "date": "23-01-2020 12:23",
    "temperature": 30
}

# wiadomość od centranego do personalnego
meet_response = {
    "room_id": 21
}

# wiadomość od technicznego do pokoju
room_power_request = {}

# wiadomość od pokoju do technicznego
room_power_response = {
    "power": 1234
}

#nie wiem czy nie brakuje od pokoju do centralnego
