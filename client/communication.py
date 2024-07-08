import json
import db
import system


def create_invite(room, address):
    message = {
        "room": str(room),
        "address": str(address),
        "key": room.key,
    }
    #print(message)
    message = json.dumps(message)
    return system.encrypt(address.key, message)

def decode_invite(data, address):
    decoded = system.decrypt(address.key, data)
    message = json.loads(decoded)
    return message

def accept_invite(invite):
    pass
