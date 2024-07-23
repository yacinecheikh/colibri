import json
import db
import system


def create_invite(room, address):
    message = {
        "room": str(room),
        #"address": str(address),
        "key": room.key,
        "auth": room.auth,
    }
    #print(message)
    message = json.dumps(message)
    return system.encrypt(address.key, message)

def decode_invite(message, address):
    # TODO: error handling (if the address is foreign)
    decoded = system.decrypt(address.key, message.data)
    message = json.loads(decoded)
    return message

