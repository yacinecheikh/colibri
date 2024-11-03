import requests
from random import choice
import argparse
import os
import sys
import json
from hashlib import sha256

import net
import db
import messaging
import rand
from datatypes import Address, Room, Message, Server, Broadcast
from crypto_module import AddressKeys, RoomKeys, BroadcastKeys


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
sub = subparsers.add_parser("add-server")
sub.add_argument("host")
sub = subparsers.add_parser("remove-server")
sub.add_argument("host")
# trusted servers can be used to select a random server for a new address
# TODO: remove this feature and let the client choose a random server instead ?
# (this may be a security problem if the client is compromised, since the cli-client is supposed to be the only critical part that needs to be audited)
# TODO: to simplify feature implementation from the frontend client, the database should allow additional metadata on each object (server, address,...)
sub = subparsers.add_parser("list-trusted-servers")
sub = subparsers.add_parser("trust-server")
sub.add_argument("host")
sub = subparsers.add_parser("untrust-server")
sub.add_argument("host")

sub = subparsers.add_parser("list-owned-addresses")
sub = subparsers.add_parser("list-foreign-addresses")  # list-foreign-addresses
sub = subparsers.add_parser("new-address")
#sub.add_argument("server")
sub.add_argument("server", nargs="?", default=None)  # optional
sub = subparsers.add_parser("remove-address")
sub.add_argument("address")
sub = subparsers.add_parser("import-address")
sub = subparsers.add_parser("export-address")
sub.add_argument("address")
# TODO: find a better name
sub = subparsers.add_parser("export-address-info")
sub.add_argument("address")


# message management
sub = subparsers.add_parser("list-messages")
sub.add_argument("address")
sub = subparsers.add_parser("remove-message")  # local
#sub.add_argument("address")
sub.add_argument("message")
sub = subparsers.add_parser("list-remote-messages")  # local db lookup
sub.add_argument("address")
sub = subparsers.add_parser("fetch-messages")  # fetch remote messages
sub.add_argument("address")
sub = subparsers.add_parser("remove-remote-messages")  # remote
sub.add_argument("address")
sub.add_argument("messages", nargs="+")  # TODO test

# actually do something with messages
# TODO: clarify what is a message and what is received by an address
# (broadcasts and rooms should also have access to the same high level features)

# for now, messages are text-only and untyped
sub = subparsers.add_parser("read-message") # the message is piped to stdin
sub.add_argument("message")
sub = subparsers.add_parser("send-message") # the message is piped to stdin
sub.add_argument("address")

## low level manipulation (intended for a user-friendly frontend)
#sub = subparsers.add_parser("send-message") # the message is piped to stdin
#sub.add_argument("address")
#
## message formatting (encoding metadata, signing,...)
#sub = subparsers.add_parser("format-message")  # text is piped to stdin
#sub.add_argument("type", choices=["text", "room-info", "address-info", "broadcast-info", "nested", "sealed", "extended"])
#sub = subparsers.add_parser("seal-message")  # text is piped to stdin
#sub.add_argument("address")
#sub = subparsers.add_parser("unseal-message")  # text is piped to stdin
#sub.add_argument("address")
#
## low level message parsing primitives
#sub = subparsers.add_parser("read-message-type")  # text is piped to stdin
#sub.add_argument("message")
#sub = subparsers.add_parser("read-message-content")  # text is piped to stdin
#sub.add_argument("message")






#sub = subparsers.add_parser("list-invites")

sub = subparsers.add_parser("list-rooms")
sub = subparsers.add_parser("new-room")
#sub.add_argument("server")
sub.add_argument("server", nargs="?", default=None)  # optional
sub = subparsers.add_parser("remove-room")
sub.add_argument("room")
sub = subparsers.add_parser("import-room")
sub = subparsers.add_parser("export-room")
sub.add_argument("room")
# view chatroom contents
sub = subparsers.add_parser("read-room")
sub.add_argument("room")
# set chatroom contents
sub = subparsers.add_parser("write-room")
sub.add_argument("room")




sub = subparsers.add_parser("list-owned-broadcasts")
sub = subparsers.add_parser("list-foreign-broadcasts")
sub = subparsers.add_parser("new-broadcast")
#sub.add_argument("server")
sub.add_argument("server", nargs="?", default=None)  # optional
sub = subparsers.add_parser("remove-broadcast")
sub.add_argument("broadcast")
sub = subparsers.add_parser("import-broadcast")
sub = subparsers.add_parser("export-broadcast")
sub.add_argument("broadcast")
sub = subparsers.add_parser("export-broadcast-info")
sub.add_argument("broadcast")
# view signed broadcast content
sub = subparsers.add_parser("read-broadcast")
sub.add_argument("broadcast")
# broadcast new signed content
sub = subparsers.add_parser("write-broadcast")
sub.add_argument("broadcast")



# other operations (TODO: sort):

# TODO: use import-address for both foreign and owned addresses
# merge with addresses
#sub = subparsers.add_parser("add-foreign-address")
#sub = subparsers.add_parser("show-address")
#sub.add_argument("address")

#sub = subparsers.add_parser("open-invite")
#sub.add_argument("address")
#sub.add_argument("message")

# send an invite message
#sub = subparsers.add_parser("send-invite")
#sub.add_argument("address", help="sent to address")
#sub.add_argument("room", help="invite to room")


# export-<address/room/broadcast>[-info] output a message ready to be sent with send-message, write-room or write-broadcast
# text messages are formatted with this command:
sub = subparsers.add_parser("text-message")  # text is piped to stdin





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
        server = db.get_server(args.host)
        if server is None:
            print(f"error: unknown server {args.host}", file=sys.stderr)
            sys.exit(1)
        db.trust_server(server)
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
            #print(address)
            if address.auth is None:
                print(address)
    case "new-address":
        keys = AddressKeys()
        auth = rand.auth()
        if args.server is not None:
            server = db.get_server(args.server)
            if server is None:
                print(f"error: server {args.server} is not known")
                sys.exit(1)
        else:
            servers = db.list_trusted_servers()
            if not servers:
                print("error: no trusted server found")
                sys.exit(1)
            server = choice(servers)
        #print(f"generating address on server {server}")
        name = net.register_address(server, auth)
        address = Address(
            name=name,
            server=server,
            auth=auth,
            keys=keys)
        db.add_address(address)
        print(address)
    case "remove-address":
        address = db.get_address(args.address)
        assert address is not None
        db.remove_address(address)
        print("ok")

    case "export-address":
        address = db.get_address(args.address)
        print(messaging.address_data(address))

    # address contact exchange
    #case "show-address":
    case "export-address-info":
        address = db.get_address(args.address)
        print(messaging.address_contact(address))

    case "import-address":
        with open("/dev/stdin") as f:
            imported = f.read()
        imported = json.loads(imported)
        #print(imported)
        address_url = imported["address"]
        name, server_url = address_url.split("@")
        address = db.get_address(address_url)
        if address is not None:
            print(f"address {address} was already imported. skipping", file=sys.stderr)
            sys.exit()
        server = db.get_server(server_url)
        if server is None:
            # the server does not need to be trusted
            #print("warning: importing address from unknown server {server}, adding {server} as trusted", file=sys.stderr)
            server = Server(
                    url=server_url,
                    #trusted=True
                    trusted=False
                    )
            db.add_server(server)
        # inefficient and ugly
        # TOOD: fix this by replacing to/from_json with to/from_dict
        keys = AddressKeys.from_json(json.dumps(imported["keys"]))
        # TODO: remove dead code after testing
        #key = system.save_key(imported["public_key"], imported["private_key"])
        address = Address(
                name=name,
                server=server,
                auth=imported["auth"] if "auth" in imported else None,
                keys=keys,
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
    case "fetch-messages":
        address = db.get_address(args.address)
        remote_messages = net.read_messages(address)
        # existing messages will not be duplicated/replaced
        # TODO: update if exists (set remote_copy = TRUE)
        for m in remote_messages:
            db.add_message(m)
        print("ok")
    case "remove-message":
        message_name, address_url = args.message.split("@", 1)
        address = db.get_address(address_url)
        message = db.get_message(address, message_name)
        db.remove_message(message)
        print("ok")
    case "remove-remote-messages":
        # TODO: use message url instead of address + message name
        address = db.get_address(args.address)
        messages = []
        for name in args.messages:
            message = db.get_message(address, name)
            if message is None:
                print(f"error: could not find message {name}", file=sys.stderr)
                sys.exit(1)
            messages.append(message)
        names = [m.name for m in messages]
        net.delete_messages(address, names)
        for m in messages:
            db.remove_remote_message(m)

        print("ok")

    case "read-message":
        # TODO: use db.get_message(args.message)
        message_name, address_name, server_url = args.message.split("@")
        address = db.get_address(f"{address_name}@{server_url}")
        message = db.get_message(address, message_name)
        decrypted = address.keys.receive(message.data)
        print(decrypted)

        #text = json.loads(decrypted)["text"]

        #payload = messaging.from_address(address, message.data)
        #print("type:", payload["type"])
        #if payload["type"] == "text":
        #    print(payload["text"])


    #case "list-invites":
    #    invites = db.list_invites()
    #    for invite in invites:
    #        # TODO: print message@address@server and room@server
    #        print(invite)
    # invites are removed along with their containing message


    case "list-rooms":
        for room in db.list_rooms():
            print(room)
    case "new-room":
        # currently, all symetric keys are AES128 random bytes
        # bytes cannot be serialized as json -> use uuid instead
        #key = os.urandom(16)
        #key = str(uuid())
        keys = RoomKeys()
        auth = rand.auth()
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
                keys=keys,
                )
        db.add_room(room)
        print(db.get_room(f"{room.name}@{room.server}"))
    case "remove-room":
        room = db.get_room(args.room)
        assert room is not None
        #if room is None:
        #    print("The selected room does not exist")
        #else:
        db.remove_room(room)
        print("ok")

    case "import-room":
        with open("/dev/stdin") as f:
            imported = f.read()
        imported = json.loads(imported)
        #print(imported)
        room_url = imported["room"]
        name, server_url = room_url.split("@")
        room = db.get_room(room_url)
        if room is not None:
            print(f"room {room} was already imported. skipping", file=sys.stderr)
            sys.exit()
        server = db.get_server(server_url)
        if server is None:
            # the server does not need to be trusted
            #print("warning: importing room from unknown server {server}, adding {server} as trusted", file=sys.stderr)
            server = Server(
                    url=server_url,
                    #trusted=True
                    trusted=False
                    )
            db.add_server(server)
        # inefficient and ugly
        # TOOD: fix this by replacing to/from_json with to/from_dict
        keys = RoomKeys.from_json(json.dumps(imported["keys"]))
        # TODO: remove dead code after testing
        #key = system.save_key(imported["public_key"], imported["private_key"])
        room = Room(
                name=name,
                server=server,
                auth=imported["auth"] if "auth" in imported else None,
                keys=keys,
                )
        db.add_room(room)
        print("ok")


    case "export-room":
        room = db.get_room(args.room)
        print(messaging.room_data(room))


    case "list-foreign-broadcasts":
        broadcasts = db.list_broadcasts()
        for b in broadcasts:
            if b.auth is None:
                print(b)
    case "list-owned-broadcasts":
        broadcasts = db.list_broadcasts()
        for b in broadcasts:
            if b.auth is not None:
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
        auth = rand.auth()
        name = net.register_broadcast(server, auth)
        keys = BroadcastKeys()
        #auth_key = gpg.create_key()
        #access_key = str(uuid())
        b = Broadcast(
                name = name,
                server = server,
                auth = auth,
                keys = keys,
                #auth_key = auth_key,
                #access_key = access_key,
                )
        db.add_broadcast(b)
        print(b)

    case "remove-broadcast":
        b = db.get_broadcast(args.broadcast)
        assert b is not None
        db.remove_broadcast(b)
        print("ok")

    case "import-broadcast":
        with open("/dev/stdin") as f:
            imported = f.read()
        imported = json.loads(imported)
        #print(imported)
        broadcast_url = imported["broadcast"]
        name, server_url = broadcast_url.split("@")
        broadcast = db.get_broadcast(broadcast_url)
        if broadcast is not None:
            print(f"broadcast {broadcast} was already imported. skipping", file=sys.stderr)
            sys.exit()
        server = db.get_server(server_url)
        if server is None:
            # the server does not need to be trusted
            #print("warning: importing broadcast from unknown server {server}, adding {server} as trusted", file=sys.stderr)
            server = Server(
                    url=server_url,
                    #trusted=True
                    trusted=False
                    )
            db.add_server(server)
        # inefficient and ugly
        # TOOD: fix this by replacing to/from_json with to/from_dict
        keys = BroadcastKeys.from_json(json.dumps(imported["keys"]))
        # TODO: remove dead code after testing
        #key = system.save_key(imported["public_key"], imported["private_key"])
        broadcast = Broadcast(
                name=name,
                server=server,
                auth=imported["auth"] if "auth" in imported else None,
                keys=keys,
                )
        db.add_broadcast(broadcast)
        print("ok")



    case "export-broadcast":
        broadcast = db.get_broadcast(args.broadcast)
        print(messaging.broadcast_data(broadcast))

    # view access
    case "export-broadcast-info":
        broadcast = db.get_broadcast(args.broadcast)
        print(messaging.broadcast_contact(broadcast))







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
    #case "add-foreign-address":
    #    address = input()
    #    name, server_url = address.split("@")
    #    server = db.get_server(server_url)
    #    if server is None:
    #        print("adding server", file=sys.stderr)
    #        db.add_server(Server(url=server_url, trusted=False))
    #        server = db.get_server(server_url)
    #    # TODO: check other usages of "if server not in db.list_servers()"

    #    public_key = sys.stdin.read()
    #    key_name = system.save_key(public_key)
    #    address = Address(
    #            name=name,
    #            server=server,
    #            auth=None,
    #            key=key_name
    #            )
    #    #print(address)
    #    db.add_address(address)
    #    #print("get:", db.get_address(str(address)))
    #    print("ok")

    # TODO: all of this has to be sorted

    # fetch updates
    #case "read-address":
    #    address = db.get_address(args.address)
    #    messages = net.read_messages(address)
    #    #print(messages)
    #    for message in messages:
    #        message = Message(
    #                name = message["id"],
    #                address = address,
    #                data = message["data"]
    #                )
    #        #print(message)
    #        if db.get_message(address, message.name):
    #            # the message was already downloaded -> skip
    #            continue
    #        decoded = gpg.receive(message)
    #        content = json.loads(decoded)
    #        # TODO: split depending on message type
    #        print(content)

    #        #db.add_message(message)

    #        #invite = messaging.decode_invite(message, address)
    #        #name, server = invite["room"].split("@")
    #        #room_file = system.create_room()
    #        #room = Room(
    #        #        name,
    #        #        server,
    #        #        invite["auth"],
    #        #        invite["key"],
    #        #        room_file,
    #        #        )
    #        #db.add_room(room)
    #        #print(room)

    # invite messages
    #case "open-invite":
    #    # TODO: rewrite (address + message name) to message url (message@address@server)
    #    address = db.get_address(args.address)
    #    message = db.get_message(address, args.message)
    #    invite = db.get_invite(message)
    #    db.add_room(invite.room)

    #case "send-invite":
    #    address = db.get_address(args.address)
    #    room = db.get_room(args.room)
    #    message = messaging.create_invite(room)
    #    encrypted = messaging.for_address(address, message)
    #    print(net.send_message(address, encrypted))

    case "send-message":
        address = db.get_address(args.address)
        data = sys.stdin.read()
        # format from text to dict
        #message = messaging.create_message(data)
        encrypted = address.keys.send(data)
        #print(encrypted)
        #encrypted = messaging.for_address(address, data)
        print(net.send_message(address, encrypted))

    # view signed broadcast content
    case "read-broadcast":
        broadcast = db.get_broadcast(args.broadcast)
        data = net.read_broadcast(broadcast)
        # uninitialized broadcasts return an empty string
        if data != "":
            decrypted = broadcast.keys.view(data)
            print(decrypted)
        #print(data)
        #decrypted = gpg.decrypt(broadcast.access_key, data)
        #print(decrypted)
        #payload = json.loads(decrypted)
        #print(payload)
        #correct_signature = gpg.verify(broadcast.auth_key, payload["data"], payload["signature"])
        #if not correct_signature:
        #    print("ERROR: incorrect signature. This broadcasted content may be corrupt, or insecure")
        #    sys.exit()
        #print(payload["data"])

        # TODO: save read content in the database, with the last fetch date
        # (create a broadcast_content table and a room_content table)

    # broadcast new signed content
    case "write-broadcast":
        broadcast = db.get_broadcast(args.broadcast)
        with open("/dev/stdin") as f:
            data = f.read()
        #print(data)
        encrypted = broadcast.keys.publish(data)
        #signature = gpg.sign(broadcast.auth_key, data)
        #broadcasted = {
        #    "data": data,
        #    "signature": signature,
        #}
        #broadcasted = json.dumps(broadcasted)
        ##print(broadcasted)
        #encrypted = gpg.encrypt(broadcast.access_key, broadcasted)
        #print(encrypted)
        print(net.write_broadcast(broadcast, encrypted))

    # view chatroom contents
    case "read-room":
        room = db.get_room(args.room)
        data = net.read_room(room)
        #print(encrypted)
        h = sha256()
        h.update(data.encode())
        room.last_hash = h.hexdigest()
        #print(type(room.last_hash))
        db.update_room_hash(room)
        #print(room.last_hash)
        # uninitialized rooms contain an empty string
        if data != "":
            data = room.keys.decrypt(data)
            print(data)
        #data = gpg.decrypt(room.key, encrypted)

    # set chatroom contents
    case "write-room":
        room = db.get_room(args.room)
        if room is None:
            print(f"error: could not find room {args.room}", file=sys.stderr)
            sys.exit(1)
        with open("/dev/stdin") as f:
            data = f.read()
        encrypted = room.keys.encrypt(data)
        #encrypted = gpg.encrypt(room.key, data)
        #print("last known hash:", room.last_hash)
        success = net.write_room(room, encrypted)
        if success:
            # update hash
            h = sha256()
            h.update(encrypted.encode())
            room.last_hash = h.hexdigest()
            db.update_room_hash(room)
            print("ok")
        else:
            print("sync error, need to read updates first")


