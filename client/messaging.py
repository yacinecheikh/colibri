"""
message processing
"""
import json

import db
from datatypes import Address
import gpg


def for_address(address: Address, message: dict):
    return gpg.send(address.key, json.dumps(message))

def from_address(address: Address, data: str):
    return json.loads(gpg.receive(address.key, message))

def for_broadcast(broadcast: Broadcast, data: str):
    signature = gpg.sign(broadcast.auth_key, data)
    broadcasted = json.dumps({
        "data": data,
        "signature": signature,
    })
    encrypted = gpg.encrypt(broadcast.access_key, broadcasted)
    return encrypted

def from_broadcast(broadcast: Broadcast, data: str):
    decrypted = gpg.decrypt(broadcast.access_key, data)
    received = json.loads(decrypted)
    signature_correct, gpg.verify(broadcast.auth_key, received["data"], received["signature"])
    return (signature_correct, received["data"])

def for_room(room: Room, data: str):
    pass

def from_room(room: Room, data: str):
    pass

def create_room_invite(room: Room):
    return json.dumps({
        "type": "room-invite",
        "room": str(room),
        "auth": room.auth,
        "key": room.key,
    })

def create_message(text, sign_key=None):
    # TODO: optionally sign with broadcast auth_key or address key
    return json.dumps({
        "type": "text",
        "text": data,
        #"signature": None,
    })

def open_message(data: str):
    message = json.loads(data)
    return message

#def open_invite(invite_data: dict):
#    name, server_url = invite_data["room"].split("@")
#    room = Room(
#            name = name,
#    pass

#def decode_invite(message, address):
#    # TODO: error handling (if the address is foreign)
#    decoded = system.decrypt(address.key, message.data)
#    message = json.loads(decoded)
#    return message

