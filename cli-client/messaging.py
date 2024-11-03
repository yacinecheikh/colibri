"""
message processing
"""
import json

import db
from datatypes import Address, Room, Broadcast, Message


# old
def for_address(address: Address, message: dict):
    return address.keys.send(json.dumps(message))
    #gpg.send(address.key, json.dumps(message))

# TODO: change the cli parameters to be able to use this function to sign
def from_address(address: Address, data: str):
    decrypted = gpg.receive(address.key, data)
    payload = json.loads(decrypted)
    return payload

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
    return gpg.encrypt(room.key, data)

def from_room(room: Room, data: str):
    return gpg.decrypt(room.key, data)




# wrapper over room/broadcast/address cryptography (ignore and use the crypto.base interface ?)

#def to_address(address, message):
#    pass
#
#def from_address(address, message):
#    # sign
#    pass
#
#def to_room(room, message):
#    pass
#
#def to_broadcast(broadcast, message):
#    pass


# chat rooms (and optionally broadcasts) have a chat history
# TODO: use a single (nested) message instead

#def read_history(

#def append(history, message):
#    pass


# decode message

def open_message(message: Message):
    #data = json.loads(message.data)
    pass


# encode message types

def message(message_body):
    # TODO: add metadata ? (data, author username,...)


    return json.dumps(message_body)

# this type of message is not freely created by the cli client
# (pipe chains are not suited to combining multiple inputs)
# TODO: reserve for special app features (copying a broadcast or a conversation into a single message)
def nested(*message_parts):
    # a single message can contain multiple elements (some text, a room-info, text, address-info, text,...)
    # this allows future extensibility to allow embedding meda,
    # email-like attachments,
    # chat histories,
    # or just sending a conversation in a message
    return {
        "type": "nested",
        "parts": list(message_parts)
    }

def text(text):
    return {
        "type": "text",
        "text": text,
    }

#def room(room: Room):
#    return {
#        "type": "room-info",
#        "room": str(room),
#        "auth": room.auth,
#        # TODO: assert the private key is known first
#        "keys": room.keys.to_json(),
#    }


# show the public keys of an address
def address_contact(address: Address):
    return json.dumps({
        "type": "address-contact",
        "address": str(address),
        # TODO: fix this
        "keys": json.loads(address.keys.public().to_json()),
    })

# export the private keys and auth password of an address
def address_data(address: Address):
    return json.dumps({
        "type": "address-data",
        "address": str(address),
        "auth": address.auth,
        # inefficient
        # TODO: fix this by not using json.dumps() in to_json() ?
        # requires a new function name (to_dict/from_dict)
        "keys": json.loads(address.keys.to_json()),
    })

#def address_info(address: Address):
#    return {
#        "type": "address-info",
#        "address": str(address),
#        "keys": address.keys.to_json(),
#    }

def room_data(room: Room):
    return json.dumps({
        "type": "room-data",
        "room": str(room),
        "auth": room.auth,
        "keys": json.loads(room.keys.to_json()),
    })

def broadcast_contact(broadcast: Broadcast):
    return json.dumps({
        "type": "broadcast-contact",
        "broadcast": str(broadcast),
        "keys": json.loads(broadcast.keys.public().to_json()),
    })

def broadcast_data(broadcast: Broadcast):
    return json.dumps({
        "type": "broadcast-data",
        "broadcast": str(broadcast),
        "auth": broadcast.auth,
        "keys": json.loads(broadcast.keys.to_json()),
    })

#def broadcast_info(broadcast: Broadcast):
#    return {
#        "type": "broadcast-info",
#        "broadcast": str(broadcast),
#        "keys": broadcast.keys.export_public().to_json(),
#    }


def create_message(text, sign_key=None):
    # TODO: optionally sign messages with broadcast auth_key or address key
    # TODO: reuse json messages in the room edition UI
    return {
        "type": "text",
        "text": text,
        #"signature": None,
    }

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

