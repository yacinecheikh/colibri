import json

import db
import system
from datatypes import Address

def address(addr: Address, data: str):
    return system.encrypt(address.key, data)

def receive(addr: Address, data: str):
    return system.decrypt(address.key, data)

def create_invite(room):
    message = {
        "room": str(room),
        #"address": str(address),
        "key": room.key,
        "auth": room.auth,
    }
    #print(message)
    message = json.dumps(message)
    return message

def decode_invite(message, address):
    # TODO: error handling (if the address is foreign)
    decoded = system.decrypt(address.key, message.data)
    message = json.loads(decoded)
    return message

