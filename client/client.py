import requests
from uuid import uuid4 as uuid
from random import choice
import argparse
import os
import sys
import json

import net
import system
import gpg
import db
import messaging
from datatypes import Address, Room, Message, Server, Broadcast


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
sub = subparsers.add_parser("import-address")
sub = subparsers.add_parser("export-address")
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
sub = subparsers.add_parser("import-room")
sub = subparsers.add_parser("export-room")
sub.add_argument("room")


sub = subparsers.add_parser("list-broadcasts")
sub = subparsers.add_parser("new-broadcast")
#sub.add_argument("server")
sub.add_argument("server", nargs="?", default=None)  # optional
sub = subparsers.add_parser("remove-broadcast")
sub.add_argument("broadcast")
sub = subparsers.add_parser("import-broadcast")
sub = subparsers.add_parser("export-broadcast")
sub.add_argument("broadcast")


# other operations (TODO: sort):

# merge with addresses
sub = subparsers.add_parser("add-foreign-address")
sub = subparsers.add_parser("show-address")
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
        key = gpg.create_key()  # asymetric key pair
        auth = str(uuid())
        server_url = args.server
        if server_url is None:
            servers = db.list_trusted_servers()
            if not servers:
                print("error: no trusted server found")
                sys.exit()
            server = choice(servers)
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

    case "export-address":
        address = db.get_address(args.address)
        exported = {
            "name": address.name,
            "server": address.server.url,
            "auth": address.auth,
        }
        with open(system.public_key(address.key)) as f:
            exported["public_key"] = f.read()
        with open(system.private_key(address.key)) as f:
            exported["private_key"] = f.read()

        print(json.dumps(exported))
    case "import-address":
        with open("/dev/stdin") as f:
            imported = f.read()
        imported = json.loads(imported)
        address_url = f'{imported["name"]}@{imported["server"]}'
        address = db.get_address(address_url)
        if address is not None:
            print(f"address {address} was already imported. skipping", file=sys.stderr)
            sys.exit()
        server = db.get_server(imported["server"])
        if server is None:
            print("warning: importing address from unknown server {server}, adding {server} as trusted", file=sys.stderr)
            server = Server(
                    url=imported["server"],
                    trusted=True
                    )
            db.add_server(server)
        key = system.save_key(imported["public_key"], imported["private_key"])
        address = Address(
                name=imported["name"],
                server=server,
                auth=imported["auth"],
                key=key,
                )
        db.add_address(address)
        print("ok")




    case "list-messages":
        address = db.get_address(args.address)
        messages = db.list_messages(address)
        for message in messages:
            print(message)
    case "list-remote-messages":
        address = db.get_address(args.address)
        messages = db.list_remote_messages(address)
        for message in messages:
            print(message)
    case "update-messages":
        address = db.get_address(args.address)
        remote_messages = net.read_messages(address)
        # existing messages will not be duplicated/replaced
        # TODO: update if exists (set remote_copy = TRUE)
        for m in remote_messages:
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
        for invite in invites:
            # TODO: print message@address@server and room@server
            print(invite)
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
            servers = db.list_trusted_servers()
            if not servers:
                print("error: no trusted server found")
                sys.exit()
            server = choice(servers)
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

    # TODO: import/export-room


    case "list-broadcasts":
        broadcasts = db.list_broadcasts()
        for b in broadcasts:
            print(b)
    case "new-broadcast":
        if args.server is None:
            servers = db.list_trusted_servers()
            if not servers:
                print("error: no trusted server found")
                sys.exit()
            server = choice(servers)
        else:
            server = db.get_server(args.server)
        auth = str(uuid())
        name = net.register_broadcast(server, auth)
        auth_key = gpg.create_key()
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

    # TODO: import/export-broadcast

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
        with open(system.public_key(address.key)) as f:
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
            decoded = gpg.receive(message)
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
        data = net.read_broadcast(broadcast)
        #print(data)
        decrypted = gpg.decrypt(broadcast.access_key, data)
        #print(decrypted)
        payload = json.loads(decrypted)
        #print(payload)
        correct_signature = gpg.verify(broadcast.auth_key, payload["data"], payload["signature"])
        if not correct_signature:
            print("ERROR: incorrect signature. This broadcasted content may be corrupt, or insecure")
            sys.exit()

        # TODO: save read content in the database, with the last fetch date
        # (create a broadcast_content table and a room_content table)

    # broadcast new signed content
    case "write-broadcast":
        broadcast = db.get_broadcast(args.broadcast)
        with open("/dev/stdin") as f:
            data = f.read()
        #print(data)
        signature = gpg.sign(broadcast.auth_key, data)
        broadcasted = {
            "data": data,
            "signature": signature,
        }
        broadcasted = json.dumps(broadcasted)
        #print(broadcasted)
        encrypted = gpg.encrypt(broadcast.access_key, broadcasted)
        #print(encrypted)
        print(net.write_broadcast(broadcast, encrypted))

    # view chatroom contents
    case "read-room":
        room = db.get_room(args.room)
        # TODO

    # set chatroom contents
    case "write-room":
        room = db.get_room(args.room)
        # TODO


