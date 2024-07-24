import requests
from uuid import uuid4 as uuid
from random import choice
import argparse
import os
import sys
import json

import net
import system
import db
import messaging
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

sub = subparsers.add_parser("list-owned-addresses")
sub = subparsers.add_parser("list-foreign-addresses")
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


# other operations (TODO: sort):

# merge with addresses
sub = subparsers.add_parser("add-foreign-address")
sub = subparsers.add_parser("show-address")
sub.add_argument("address")
sub = subparsers.add_parser("import-address")
sub = subparsers.add_parser("export-address")
sub.add_argument("address")


# fetch new messages
sub = subparsers.add_parser("read-address")  # server interaction
sub.add_argument("address")

sub = subparsers.add_parser("open-invite")
sub.add_argument("address")
sub.add_argument("message")

# send an invite message
sub = subparsers.add_parser("send-invite")
sub.add_argument("address", help="sent to address")
sub.add_argument("room", help="invite to room")

# send a text message
sub = subparsers.add_parser("send-message") # the message is piped to stdin
sub.add_argument("address")



# view signed broadcast content
sub = subparsers.add_parser("read-broadcast")
sub.add_argument("broadcast")
# broadcast new signed content
sub = subparsers.add_parser("write-broadcast")
sub.add_argument("broadcast")



# view chatroom contents
sub = subparsers.add_parser("read-room")
sub.add_argument("room")
# set chatroom contents
sub = subparsers.add_parser("write-room")
sub.add_argument("room")




args = parser.parse_args()

#print(args)

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

    # addresses

    case "list-owned-addresses":
        addresses = db.list_addresses()
        for address in addresses:
            if address.auth is not None:
                print(address)
    case "list-foreign-addresses":
        addresses = db.list_addresses()
        for address in addresses:
            if address.auth is None:
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
        print(db.get_room(f"{room.name}@{room.server}"))
    case "remove-room":
        room = db.get_room(args.room)
        if room is None:
            print("The selected room does not exist")
        else:
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

    # TODO: sort all these operations

    # address contact exchange
    case "show-address":
        # output:
        # <address@server>
        # BEGIN PGP PUBLIC KEY
        # …
        # END PGP PUBLIC KEY
        address = db.get_address(args.address)
        print(address)
        # TODO: move this path formatting to system (system.find_public(key_name) for example)
        with open(f'data/keys/{address.key}.public.asc') as f:
            print(f.read())
    case "add-foreign-address":
        address = input()
        name, server = address.split("@")
        server = Server(url=server, trusted=False)
        # TODO: test, should use Server.__eq__()
        # TODO: check other usages of "if server not in db.list_servers()"
        if server not in db.list_servers():
            db.add_server(server)
        public_key = sys.stdin.read()
        key_name = system.save_key(public_key)
        address = Address(
                name=name,
                server=server,
                auth=None,
                key=key_name
                )
        db.add_address(address)
        print("ok")

    # private key export
    case "export-owned-address":
        address = db.get_address(args.address)
        exported = {
            "name": address.name,
            "server": address.server.url,
            "auth": address.auth,
        }
        with open(f"data/keys/{address.key}.public.asc") as f:
            exported["public_key"] = f.read()
        with open(f"data/keys/{address.key}.private.asc") as f:
            exported["private_key"] = f.read()

        print(json.dumps(exported))
    case "import-owned-address":
        # TODO after checking export works
        pass

    # TODO: all of this has to be sorted

    # fetch updates
    case "read-address":
        # <id>@<server>
        url = args.address
        address = db.get_address(url)
        messages = net.read_messages(address)
        #print(messages)
        for message in messages:
            message = Message(
                    message["id"],
                    address,
                    message["data"]
                    )
            #print(message)
            if db.get_message(address, message.name):
                # the message was already downloaded -> skip
                continue
            decoded = system.decrypt(message)
            content = json.loads(decoded)
            # TODO: split depending on message type
            print(content)

            #db.add_message(message)

            #invite = messaging.decode_invite(message, address)
            #name, server = invite["room"].split("@")
            #room_file = system.create_room()
            #room = Room(
            #        name,
            #        server,
            #        invite["auth"],
            #        invite["key"],
            #        room_file,
            #        )
            #db.add_room(room)
            #print(room)

    # invite messages
    case "open-invite":
        # TODO: rewrite (address + message name) to message url (message@address@server)
        address = db.get_address(args.address)
        message = db.get_message(address, args.message)
        invite = db.get_invite(message)
        db.add_room(invite.room)

    case "send-invite":
        address = db.get_address(args.address)
        room = db.get_room(args.room)
        # TODO: encrypt(json({type: invite, invite: {}}))
        invite = messaging.create_invite(room)
        print(invite)
        sent = messaging.address(address, invite)
        net.send_message(address, sent)

    case "send-message":
        address = db.get_address(args.address)
        data = sys.stdin.read()
        # TODO

    # view signed broadcast content
    case "read-broadcast":
        broadcast = db.get_broadcast(args.broadcast)
        # TODO

    # broadcast new signed content
    case "write-broadcast":
        broadcast = db.get_broadcast(args.broadcast)
        # TODO

    # view chatroom contents
    case "read-room":
        room = db.get_room(args.room)
        # TODO

    # set chatroom contents
    case "write-room":
        room = db.get_room(args.room)
        # TODO


