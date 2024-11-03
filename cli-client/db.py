import sqlite3

from datatypes import (
        Server, Room, Address, Broadcast, Message,
        RoomInfo, AddressInfo, BroadcastInfo,
        )
from crypto_module import *


db = sqlite3.connect("data.sqlite3")

# initialize table structures
with open("init.sql") as f:
    db.executescript(f.read())

def query(*args):
    "wrapper over sqlite connection methods"
    cursor = db.execute(*args)
    results = cursor.fetchall()
    db.commit()
    return results


"""
db operations
"""

# servers

def list_servers():
    rows = query("""
    select id, url, trusted from server
    """)
    servers = []
    for (id, url, trusted) in rows:
        servers.append(Server(
            id = id,
            url = url,
            trusted = trusted,
            ))
    return servers

def list_trusted_servers():
    rows = query("""
    select id, url from server
    where trusted is true
    """)
    servers = []
    for (id, url) in rows:
        servers.append(Server(id=id, url=url, trusted=True))
    return servers


def get_server(url):
    rows = query("""
    select id, url, trusted
    from server
    where url = ?
    """, [url])
    if not rows:
        return None
    (id, url, trusted) = rows[0]
    return Server(id=id, url=url, trusted=trusted)


# add if not already present and return id
def add_server(server):
    existing = query("""
    select id
    from server
    where url = ?
    """, [server.url])
    if existing:
        return existing[0][0]

    inserted = query("""
    insert into server (url, trusted)
    values (?, ?)
    returning id
    """, [server.url, server.trusted])
    return inserted[0][0]


def trust_server(server):
    query("""
    update server
    set trusted = true
    where url = ?
    """, [server.url])


def untrust_server(server):
    query("""
    update server
    set trusted = false
    where url = ?
    """, [server.url])

def remove_server(server):
    query("""
    delete from server
    where id = ?
    """, [server.id])


# addresses

def list_addresses():
    rows = query("""
    select
        address.id,
        address.name,
        server.url,
        address.auth,

        address.keys
    from address
    join server
    on address.server = server.id
    """)
    addresses = []
    for (id, name, url, auth, keys) in rows:
        server = get_server(url)
        keys = AddressKeys.from_json(keys)
        address = Address(id=id, name=name, server=server, auth=auth, keys=keys)
        addresses.append(address)
    return addresses

# TODO: add bounds checks for getters ([0])
def get_address(url):
    name, server = url.split('@')
    rows = query("""
    select
        address.id,
        address.name,
        server.url,
        address.auth,
        address.keys
    from address
    join server
    on address.server = server.id

    where address.name = ? and server.url = ?
    """, [name, server])
    if not rows:
        return None

    (id, name, url, auth, keys) = rows[0]
    server = get_server(url)
    keys = AddressKeys.from_json(keys)
    address = Address(id=id, name=name, server=server, auth=auth, keys=keys)
    return address

def add_address(address: Address):
    # safety check before inserting
    # + return the id for further foreign key insertions
    existing = query("""
    select id
    from address
    where name = ? and server = ?
    """, [address.name, address.server.id])
    if existing:
        #print("existing")
        return existing[0][0]

    inserted = query("""
    insert into address (name, server, auth, keys)
    values (?, ?, ?, ?)
    returning id
    """, [address.name, address.server.id, address.auth, address.keys.to_json()])
    #print("inserted")
    return inserted[0][0]

def remove_address(address: Address):
    query("""
    delete from address
    where id = ?
    """, [address.id])


# messages

def list_messages(address: Address):
    result = query("""
    select id, name, data, remote_copy from message
    where message.address = ?
    """, [address.id])
    messages = []
    for (id, name, data, remote) in result:
        messages.append(Message(
            id=id,
            name=name,
            address=address,
            data=data,
            remote=bool(remote),
            ))
    return messages

def list_remote_messages(address: Address):
    return [m for m in list_messages(address) if m.remote]

def add_message(message: Message):
    address_id = add_address(message.address)
    existing = query("""
    select id
    from message
    where name = ? and address = ?
    """, [message.name, address_id])
    if existing:
        return existing[0][0]

    inserted = query("""
    insert into message (address, name, data, remote_copy)
    values (?, ?, ?, ?)
    returning id
    """, [address_id, message.name, message.data, message.remote])
    return inserted[0][0]

def get_message(address: Address, message_name):
    rows = query("""
    select id, data, remote_copy from message
    where address = ? and name = ?
    """, [address.id, message_name])
    if rows:
        id, data, remote = rows[0]
        return Message(
                id=id,
                name=message_name,
                data=data,
                address=address,
                remote=remote
                )

def remove_message(message: Message):
    query("""
    delete from message
    where id = ?
    """, [message.id])

def remove_remote_message(message: Message):
    query("""
    update message
    set remote_copy = false
    where id = ?
    """, [message.id])


# rooms

def list_rooms():
    rows = query("""
    select
        room.id,
        room.name,
        server.url,
        room.auth,
        room.keys,
        room.last_hash
    from room
    join server
    on room.server = server.id
    """)
    rooms = []
    for (id, name, url, auth, keys, last_hash) in rows:
        room = Room(
            id=id,
            name=name,
            server=get_server(url),
            auth=auth,
            keys=RoomKeys.from_json(keys),
            last_hash=last_hash,
        )
        rooms.append(room)
    return rooms

def get_room(url: str):
    name, server = url.split('@')
    result = query("""
    select
        room.id,
        room.name,
        server.url,
        room.auth,
        room.keys,
        room.last_hash
    from room
    join server
    on room.server = server.id

    where room.name = ? and server.url = ?
    """, [name, server])
    if not result:
        return None
    (id, name, url, auth, keys, last_hash) = result[0]
    room = Room(
            id=id,
            name=name,
            server=get_server(url),
            auth=auth,
            keys=RoomKeys.from_json(keys),
            last_hash=last_hash,
        )
    return room


def add_room(room: Room):
    existing = query("""
    select id
    from room
    where name = ? and server = ?
    """, [room.name, room.server.id])
    if existing:
        return existing[0][0]
    inserted = query("""
    insert into room (name, server, auth, keys)
    values (?, ?, ?, ?)
    returning id
    """, [room.name, room.server.id, room.auth, room.keys.to_json()])
    return inserted[0][0]

def remove_room(room: Room):
    query("""
    delete from room
    where id = ?
    """, [room.id])


def update_room_hash(room: Room):
    query("""
    update room
    set last_hash = ?
    where id = ?
    """, [room.last_hash, room.id])



# broadcasts

def list_broadcasts():
    rows = query("""
    select
        broadcast.id,
        broadcast.name,
        server.url,
        broadcast.auth,
        broadcast.keys
    from broadcast
    join server
    on broadcast.server = server.id
    """)
    broadcasts = []
    for row in rows:
        (id, name, url, auth, keys) = row
        b = Broadcast(
            id=id,
            name=name,
            server=get_server(url),
            auth=auth,
            keys=BroadcastKeys.from_json(keys),
        )
        broadcasts.append(b)
    return broadcasts

def get_broadcast(url):
    name, server = url.split("@")
    server = get_server(server)
    rows = query("""
    select id, name, auth, keys
    from broadcast
    where name = ? and server = ?
    """, [name, server.id])
    if not rows:
        return None

    row = rows[0]
    id, name, auth, keys = row
    return Broadcast(
            id = id,
            name = name,
            server = server,
            auth = auth,
            keys = BroadcastKeys.from_json(keys),
            )

def add_broadcast(broadcast: Broadcast):
    existing = query("""
    select id from broadcast
    where name = ? and server = ?
    """, [broadcast.name, broadcast.server.id])
    if existing:
        return existing[0][0]

    inserted = query("""
    insert into broadcast (name, server, auth, keys)
    values (?, ?, ?, ?)
    returning id
    """, [broadcast.name, broadcast.server.id, broadcast.auth, broadcast.keys.to_json()])
    return inserted[0][0]

def remove_broadcast(broadcast: Broadcast):
    query("""
    delete from broadcast
    where id = ?
    """, [broadcast.id])


# TODO: room/broadcast/address access info


# invites

# TODO: find a way to shorten this join
# (get db object by id ? require address ? iterate over messages ? use message@addr@host syntax ?)
# (for addr in list_addresses(): for message in list_messages():)
#def list_invites():
#    entries = query("""
#    select
#        invite.id,
#        invite.room_name,
#        invite.room_server,
#        invite.room_auth,
#        invite.room_key,
#
#        message.name,
#        address.name,
#        server.url
#    from invite
#
#    join message
#    on invite.message = message.id
#
#    join address
#    on message.address = address.id
#
#    join server
#    on address.server = server.id
#    """)
#    invites = []
#    for (id, room_name, room_serv, room_auth, room_key, message_name, address_name, server_url) in entries:
#        address = get_address(f"{address_name}@{server_url}")
#        message = get_message(address, message_name)
#
#        # TODO: get server if it exists (in case the server is trusted)
#        server = Server(url=room_serv, trusted=False)
#        room = Room(name=room_name, server=server, auth=room_auth, key=room_key)
#        invites.append(Invite(id=id, room=room))
#
#    return invites

#def get_invite(message: Message):
#    row = query("""
#    select id, room_name, room_server, room_auth, room_key
#    from invite
#    where message = ?
#    """, [message.id])[0]
#    id, name, server, auth, key = row
#    room = Room(name=name, server=Server(url=server), auth=auth, key=key)
#    invite = Invite(
#            id=id,
#            room=room,
#            )
#
#    return invite

#def remove_invite(message: Message):
#    query("""
#    delete from invite
#    where message = ?
#    """, [message.id])



