import requests
from datatypes import Room, Address


def post(endpoint, data):
    return requests.post(endpoint, json=data).json()
def get(endpoint, data):
    return requests.get(endpoint, json=data).json()
def delete(endpoint, data):
    return requests.delete(endpoint, json=data).json()


def register_room(server, auth):
    store = post(f'{server}/room/register', {
        'auth': auth,
    })
    return store

def register_address(server, auth):
    address = post(f'{server}/address/register', {
        'auth': auth,
    })
    return address


# TODO: test
def read_room(room: Room):
    return get(f"{room.server}/room/{room.name}", {
        "auth": room.auth,
    })

def write_room(room: Room, data):
    return post(f"{room.server}/room/{room.name}", {
        "auth": room.auth,
        "data": data,
    })

def read_messages(address: Address):
    return get(f"{address.server}/address/{address.name}", {
        "auth": address.auth,
    })

def delete_messages(address: Address, message_names):
    return delete(f"{address.server}/address/{address.name}", {
        "auth": address.auth,
        "messages": message_names,
    })

