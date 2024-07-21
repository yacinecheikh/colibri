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
from datatypes import Address, Room, Message, Server


# alternative to arg parsing: use an stdin script ? (while true: input())
parser = argparse.ArgumentParser(
        prog="client.py",
        description="Colibri CLI client")

subparsers = parser.add_subparsers(
        dest="command",
        help='command',
        required=True,
        )
"""
subparsers
"""

# CRUD for servers, addresses, address messages, invites, rooms and broadcasts
sub = subparsers.add_parser("list-servers")
sub = subparsers.add_parser("list-trusted-servers")
sub = subparsers.add_parser("add-server")
sub.add_argument("host")
sub = subparsers.add_parser("trust-server")
sub.add_argument("host")
sub = subparsers.add_parser("untrust-server")
sub.add_argument("host")
sub = subparsers.add_parser("remove-server")
sub.add_argument("host")


sub = subparsers.add_parser("list-addresses")
sub = subparsers.add_parser("new-address")
#sub.add_argument("server")
sub.add_argument("server", nargs="?", default=None)  # optional
sub = subparsers.add_parser("remove-address")
sub.add_argument("address")


sub = subparsers.add_parser("list-messages")
sub.add_argument("address")
sub = subparsers.add_parser("list-remote-messages")  # local db lookup
sub.add_argument("address")
sub = subparsers.add_parser("update-messages")  # fetch remote messages
sub.add_argument("address")
sub = subparsers.add_parser("remove-message")  # local
sub.add_argument("address")
sub.add_argument("message")
sub = subparsers.add_parser("remove-remote-messages")  # remote
sub.add_argument("address")
sub.add_argument("messages", nargs="+")  # TODO test

sub = subparsers.add_parser("list-invites")

sub = subparsers.add_parser("list-rooms")
sub = subparsers.add_parser("new-room")
#sub.add_argument("server")
sub.add_argument("server", nargs="?", default=None)  # optional
sub = subparsers.add_parser("remove-room")
sub.add_argument("room")


sub = subparsers.add_parser("list-broadcasts")
sub = subparsers.add_parser("new-broadcast")
#sub.add_argument("server")
sub.add_argument("server", nargs="?", default=None)  # optional
sub = subparsers.add_parser("remove-broadcast")
sub.add_argument("broadcast")


# operations:

# TODO: rename the operations
# import/export: owned address
# show/???: foreign address
# import foreign address/export known address
sub = subparsers.add_parser("import-address")
# TODO: find a syntax to export/import owned addresses
#sub.add_argument("auth", nargs="?", default=None)

sub = subparsers.add_parser("export-address")
sub.add_argument("address")



# fetch new messages at address
# open invite (from message)
# send invite (to room) at address
# send message at address

sub = subparsers.add_parser("read-address")  # server interaction
sub.add_argument("address")

sub = subparsers.add_parser("open-invite")
sub.add_argument("address")
sub.add_argument("message")

# invite messages
sub = subparsers.add_parser("send-invite")
sub.add_argument("address", help="sent to address")
sub.add_argument("room", help="invite to room")

# text messages
sub = subparsers.add_parser("send-message") # the message is piped to stdin
sub.add_argument("address")


# view signed broadcast content
# broadcast new signed content

sub = subparsers.add_parser("read-broadcast")
sub.add_argument("broadcast")
sub = subparsers.add_parser("write-broadcast")
sub.add_argument("broadcast")


# view chatroom contents
# set chatroom contents

sub = subparsers.add_parser("read-room")
sub.add_argument("room")
sub = subparsers.add_parser("write-room")
sub.add_argument("room")




# TODO: remove
# helpers
sub = subparsers.add_parser("read-addresses")
# used by humans
sub = subparsers.add_parser("describe")




args = parser.parse_args()


match args.command:
    case "list-servers":
        servers = db.list_servers()
        for server in servers:
            print(server)
    case "list-trusted-servers":
        servers = db.list_trusted_servers()
        for server in servers:
            print(server)
    case "add-server":
        server = Server(url=args.host)
        db.add_server(server)
    case "trust-server":
        db.trust_server(db.get_server(args.host))
    case "untrust-server":
        db.untrust_server(db.get_server(args.host))
    case "remove-server":
        db.remove_server(db.get_server(args.host))


    case "list-addresses":
        for address in db.list_addresses():
            print(address)
    case "new-address":
        key = system.create_key()  # asymetric key pair
        auth = str(uuid())
        server_url = args.server
        if server_url is None:
            server = choice(db.list_servers())
        else:
            server = db.get_server(server_url)
        #print(f"generating address on server {server}")
        name = net.register_address(server, auth)
        address = Address(
            name,
            server,
            auth,
            key)
        db.add_address(address)
        print(address)
    case "remove-address":
        address = db.get_address(args.address)
        db.remove_address(address)


    case "list-messages":
        address = db.get_address(args.address)
        messages = db.list_messages(address)
        print(messages)
    case "list-remote-messages":
        address = db.get_address(args.address)
        messages = db.list_remote_messages(address)
        print(messages)
    case "update-messages":
        address = db.get_address(args.address)
        remote_messages = net.read_messages(address)
        # existing messages will not be duplicated/replaced
        # TODO: update if exists (set remote_copy = TRUE)
        for m in remote_message:
            db.add_message(m)
    case "remove-message":
        address = db.get_address(args.address)
        message = db.get_message(address, args.message)
        db.remove_message(message)
    case "remove-remote-messages":
        address = db.get_address(args.address)
        # TODO: add validation
        net.delete_messages(address, args.messages)


    case "list-invites":
        invites = db.list_invites()
        print(invites)
    # invites are removed along with their containing message


    case "list-rooms":
        for room in db.list_rooms():
            print(room)
    case "new-room":
        # currently, all symetric keys are AES128 random bytes
        # bytes cannot be serialized as json -> use uuid instead
        #key = os.urandom(16)
        key = str(uuid())
        auth = str(uuid())
        server = args.server
        if server is None:
            server = choice(db.list_servers())
        else:
            server = db.get_server(server)
        #print(f"generating room on server {server}")
        name = net.register_room(server, auth)
        room = Room(
                name=name,
                server=server,
                auth=auth,
                key=key,
                )
        db.add_room(room)
        print(room)
    case "remove-room":
        room = db.get_room(args.room)
        db.remove_room(room)


    case "list-broadcasts":
        broadcasts = db.list_broadcasts()
        for b in broadcasts:
            print(b)
    case "new-broadcast":
        if args.server is None:
            server = choice(db.list_servers())
        else:
            server = db.get_server(args.server)
        auth = str(uuid())
        name = net.register_broadcast(server, auth)
        auth_key = system.create_key()
        access_key = str(uuid())
        b = Broadcast(
                name = name,
                server = server,
                auth = auth,
                auth_key = auth_key,
                access_key = access_key,
                )
        db.add_broadcast(b)
    case "remove-broadcast":
        b = db.get_broadcast(args.broadcast)
        db.remove_broadcast(b)


"""
# operations:

# TODO: rename the operations
# import/export: owned address
# show/???: foreign address
# import foreign address/export known address
sub = subparsers.add_parser("import-address")
# TODO: find a syntax to export/import owned addresses
#sub.add_argument("auth", nargs="?", default=None)

sub = subparsers.add_parser("export-address")
sub.add_argument("address")



# fetch new messages at address
# open invite (from message)
# send invite (to room) at address
# send message at address

sub = subparsers.add_parser("read-address")  # server interaction
sub.add_argument("address")

sub = subparsers.add_parser("open-invite")
sub.add_argument("address")
sub.add_argument("message")

# invite messages
sub = subparsers.add_parser("send-invite")
sub.add_argument("address", help="sent to address")
sub.add_argument("room", help="invite to room")

# text messages
sub = subparsers.add_parser("send-message") # the message is piped to stdin
sub.add_argument("address")


# view signed broadcast content
# broadcast new signed content

sub = subparsers.add_parser("read-broadcast")
sub.add_argument("broadcast")
sub = subparsers.add_parser("write-broadcast")
sub.add_argument("broadcast")


# view chatroom contents
# set chatroom contents

sub = subparsers.add_parser("read-room")
sub.add_argument("room")
sub = subparsers.add_parser("write-room")
sub.add_argument("room")




# TODO: remove
# helpers
sub = subparsers.add_parser("read-addresses")
# used by humans
sub = subparsers.add_parser("describe")




"""





#print(args)

# helpers

match args.command:
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

