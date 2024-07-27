import requests
from datatypes import Room, Address, Server, Message, Broadcast

from typing import List


def post(endpoint, data):
    return requests.post(endpoint, json=data).json()
def get(endpoint, data):
    return requests.get(endpoint, json=data).json()
def delete(endpoint, data):
    return requests.delete(endpoint, json=data).json()


def register_room(server: Server, auth):
    room = post(f'{server.url}/room/register', {
        'auth': auth,
    })
    return room

def register_address(server: Server, auth):
    address = post(f'{server.url}/address/register', {
        'auth': auth,
    })
    return address

def register_broadcast(server: Server, auth):
    broadcast = post(f'{server.url}/broadcast/register', {
        'auth': auth,
    })
    return broadcast


def read_room(room: Room):
    return get(f"{room.server.url}/room/{room.name}", {
        "auth": room.auth,
    })

def write_room(room: Room, data):
    return post(f"{room.server.url}/room/{room.name}", {
        "auth": room.auth,
        "data": data,
        "last_hash": room.last_hash,
    })


def read_broadcast(b: Broadcast):
    return get(f"{b.server.url}/broadcast/{b.name}", {})

def write_broadcast(b: Broadcast, data):
    return post(f"{b.server.url}/broadcast/{b.name}", {
        "auth": b.auth,
        "data": data
    })


def read_messages(address: Address):
    data = get(f"{address.server.url}/address/{address.name}", {
        "auth": address.auth,
    })
    messages = []
    for entry in data:
        messages.append(Message(
            name = entry["id"],
            data = entry["data"],
            ))
    return messages

def send_message(address: Address, data):
    return post(f"{address.server.url}/address/{address.name}", {
        "data": data,
    })

def delete_messages(address: Address, message_names: List[str]):
    return delete(f"{address.server.url}/address/{address.name}", {
        "auth": address.auth,
        "messages": message_names,
    })

