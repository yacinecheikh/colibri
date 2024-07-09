import requests
from uuid import uuid4 as uuid
from random import choice
import argparse
import os
import sys

import net
import system
import db
import communication
from datatypes import Address, Room, Message


# alternative to arg parsing: use an stdin script ? (while true: input())
parser = argparse.ArgumentParser(
        prog="client.py",
        description="Colibri CLI client")

subparsers = parser.add_subparsers(
        dest="command",
        help='command',
        required=True,
        )
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

sub = subparsers.add_parser("send-invite")
sub.add_argument("address", help="sent to address")
sub.add_argument("room", help="invite to room")

sub = subparsers.add_parser("delete-message")
sub.add_argument("message")

sub = subparsers.add_parser("read-room")
sub.add_argument("room")

sub = subparsers.add_parser("write-room")
sub.add_argument("room")


# used by humans
sub = subparsers.add_parser("describe")



sub = subparsers.add_parser("import-address")
# TODO: find a syntax to export/import owned addresses
#sub.add_argument("auth", nargs="?", default=None)

sub = subparsers.add_parser("export-address")
sub.add_argument("address")



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


    case "describe":
        print("servers:")
        servers = db.list_servers()
        for s in servers:
            print(s)

        print("rooms:")
        rooms = db.list_rooms()
        for r in rooms:
            print(r)

        print('addresses:')
        for a in db.list_addresses():
            if a.auth:
                print(f"{a}\t(owned)")
            else:
                print(f'{a}\t(foreign)')

    # config
    case "add-server":
        db.add_server(args.host)

    case "import-address":
        address = input()
        name, server = address.split("@")
        key = sys.stdin.read()
        key_name = system.save_key(key)
        address = Address(
                name,
                server,
                auth=None,
                key=key_name
                )
        db.add_address(address)
        print("ok")

    case "export-address":
        address = db.get_address(args.address)
        print(address)
        with open(f'data/keys/{address.key}.public.asc') as f:
            print(f.read())

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
        #key = os.urandom(16)
        # bytes cannot be serialized as json
        key = str(uuid())
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
        for address in db.list_addresses():
            messages = net.read_messages(address)
            print(f"{address}:")
            #print(messages)
            for message in messages:
                invite = communication.decode_invite(message, address)
                print(invite)

    case "read-address":
        # <id>@<server>
        url = args.address
        address = db.get_address(url)
        messages = net.read_messages(address)
        #print(messages)
        messages = net.read_messages(address)
        for message in messages:
            message = Message(
                    message["id"],
                    address,
                    message["data"]
                    )
            #print(message)
            db.add_message(message)
            invite = communication.decode_invite(message, address)
            name, server = invite["room"].split("@")
            room_file = system.create_room()
            room = Room(
                    name,
                    server,
                    invite["auth"],
                    invite["key"],
                    room_file,
                    )
            db.add_room(room)
            print(room)

    # TODO: store messages in the database and link an id with their source server+id
    #case "delete-message":
    #    message = args.message
    #    net.delete_messages(

    case "send-invite":
        room = db.get_room(args.room)
        address = db.get_address(args.address)
        invite = communication.create_invite(room, address)
        net.send_message(address, invite)
        print("ok")

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

