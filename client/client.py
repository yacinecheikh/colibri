import requests
from uuid import uuid4 as uuid
from random import choice
import argparse
import os

import net
import system
import db
from datatypes import Address, Room


# alternative to arg parsing: use an stdin script ? (while true: input())
parser = argparse.ArgumentParser(
        prog="client.py",
        description="Colibri CLI client")

subparsers = parser.add_subparsers(
        dest="command",
        help='command',
        required=True,
        )
#send_invite_parser = subparsers.add_parser("send-invite")
# subparsers
sub = subparsers.add_parser("add-server")
sub.add_argument("host")

sub = subparsers.add_parser("list-servers")

sub = subparsers.add_parser("new-address")
sub.add_argument("server", nargs="?", default=None)  # optional

sub = subparsers.add_parser("list-addresses")

sub = subparsers.add_parser("new-room")
sub.add_argument("server", nargs="?", default=None)  # optional

sub = subparsers.add_parser("list-rooms")

sub = subparsers.add_parser("read-addresses")

sub = subparsers.add_parser("read-address")
sub.add_argument("address")

sub = subparsers.add_parser("clean-address")
sub.add_argument("address")

sub = subparsers.add_parser("read-room")
sub.add_argument("room")

sub = subparsers.add_parser("write-room")
sub.add_argument("room")



args = parser.parse_args()


#print(args)

match args.command:
    # print
    case "list-servers":
        print("\n".join(db.list_servers()))
    case "list-invites":
        pass
    case "list-addresses":
        for address in db.list_addresses():
            print(address)
    case "list-rooms":
        for room in db.list_rooms():
            print(room)

    # config
    case "add-server":
        db.add_server(args.host)

    # server interaction
    case "new-address":
        key_name = system.create_key()
        auth = str(uuid())
        server = args.server
        if server is None:
            server = choice(db.list_servers())
        #print(f"generating address on server {server}")
        name = net.register_address(server, auth)
        address = Address(
            name,
            server,
            auth,
            key_name)
        db.add_address(address)
        print(address)
    case "new-room":
        # currently, all symetric keys are AES128 random bytes
        # AES128 -> 16 random bytes
        key = os.urandom(16)
        auth = str(uuid())
        server = args.server
        if server is None:
            server = choice(db.list_servers())
        #print(f"generating room on server {server}")
        name = net.register_room(server, auth)
        room_file = system.create_room()
        room = Room(
                name,
                server,
                auth,
                key,
                room_file
                )
        db.add_room(room)
        print(room)

    # fetch updates for one address
    case "read-addresses":
        for (name, server) in db.list_addresses():
            # TODO: remove the [1] (["auth"] instead)
            auth = db.get_address(name, server)[1]
            # TODO: decrypt invites (encrypted json)
            messages = net.read_messages(name, server, auth)
            print(f"{name}@{server}:")
            print(messages)

    case "read-address":
        address = args.address
        name, server = address.split("@")
        # TODO: make this readable
        # TODO: (convert db output to json)
        auth = db.get_address(name, server)[1]
        messages = net.read_messages(name, server, auth)
        # TODO: decrypt invites (encrypted json)
        print(messages)

    case "send-invite":
        pass

    # fetch updates
    case "pull":
        pass
    # message interactions
    case "read-room":
        pass
    case "write-room":
        pass
    case "accept-invite":
        pass




keys = {}

def get(endpoint, data):
    response = requests.get(endpoint, json=data)
    return response.json()

def post(endpoint, data):
    return requests.post(endpoint, json=data).json()



message_addresses = {}

stores = {}

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

