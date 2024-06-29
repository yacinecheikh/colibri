import requests
from uuid import uuid4 as uuid
from random import choice
import argparse

import net
from system import syscall
import db


# alternative to arg parsing: use an stdin script ? (while true: input())
parser = argparse.ArgumentParser(
        prog="client.py",
        description="Colibri CLI client")

parser.add_argument("command", choices=["list-servers", "list-invites", "list-addresses", "list-rooms"])
subparsers = parser.add_subparsers()
#send_invite_parser = subparsers.add_parser("send-invite")

args = parser.parse_args()


match args.command:
    case "list-servers":
        print("listing servers...")
        print(db.list_servers())
    case default:
        pass




keys = {}


def create_key():
    # TODO: assert does not exist on a fs
    name = str(uuid())
    syscall('./sgpg/create-key keys/{name}')


def get(endpoint, data):
    response = requests.get(endpoint, json=data)
    return response.json()

def post(endpoint, data):
    return requests.post(endpoint, json=data).json()



message_addresses = {}

stores = {}




def generate_keys():
    keyname = str(uuid())
    pass




def generate_message_address():
    auth = str(uuid())
    server = choice(servers)

    address = post(f"{server}/message/register", {
        "auth": auth,
    })

    message_addresses[(address, server)] = {
        'address': address,
        'server': server,
        "auth": auth,
    }
    return (address, server)

def generate_store():
    auth = str(uuid())
    server = choice(servers)
    symetric_key = str(uuid())
    address = post(f"{server}/store/register", {
        "auth": auth,
    })

    stores[(address, server)] = {
        'address': address,
        'server': server,
        "auth": auth,
        'key': symetric_key,
    }
    return (address, server)

def fetch_messages(address, server):
    auth = message_addresses[(address, server)]["auth"]
    messages = get(f"{server}/message/{address}")
    for message in messages:
        t
    return messages



def send_invite_message(address, server):
    store_address, store_server = generate_store()
    message = {
        'type': 'invite',
        'address': store_address,
        'server': store_server,
        'key': symetric_key,
    }






"""
message
"""

#message_auth = str(uuid())
#
#post('message/register')
#message_address = post('/message/register', {
#    'auth': message_auth,
#})
#
#get(f'message/{message_address}', {
#    'auth': message_auth,
#})
#
#post(f'message/{message_address}', {
#    'data': 'hi',
#})
#
#messages = get(f'message/{message_address}', {
#    'auth': message_auth,
#})
#
#ids = [message['id'] for message in messages]



"""
store
"""

#store_auth = str(uuid())
#
#post('store/register')
#
#store_address = post('store/register', {
#    'auth': store_auth,
#})
#
#get(f'store/{store_address}')
#get(f'store/{store_address}', {
#    'auth': store_auth,
#})
#
#post(f'store/{store_address}')
#post(f'store/{store_address}', {
#    'auth': store_auth,
#    'data': 'storage',
#})
#
#get(f'store/{store_address}', {
#    'auth': store_auth,
#})

