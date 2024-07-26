import sqlite3

from datatypes import Room, Address, Server, Message, Invite, Broadcast


db = sqlite3.connect("data/db.sqlite3")

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
    row = query("""
    select id, url, trusted
    from server
    where url = ?
    """, [url])[0]
    (id, url, trusted) = row
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
    insert into server (url)
    values (?)
    returning id
    """, [server.url])
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
    addresses = query("""
    select
        address.name,
        server.url,
        address.auth,
        address.key_name
    from address
    join server
    on address.server = server.id
    """)
    addresses = [Address(*address) for address in addresses]
    for address in addresses:
        address.server = get_server(address.server)
    return addresses

# TODO: add bounds checks for getters ([0])
def get_address(url):
    name, server = url.split('@')
    (id, name, url, auth, key) = query("""
    select
        address.id,
        address.name,
        server.url,
        address.auth,
        address.key_name
    from address
    join server
    on address.server = server.id

    where address.name = ? and server.url = ?
    """, [name, server])[0]
    server = get_server(url)
    address = Address(id=id, name=name, server=server, auth=auth, key=key)
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
        return existing[0][0]

    inserted = query("""
    insert into address (name, server, auth, key_name)
    values (?, ?, ?, ?)
    returning id
    """, [address.name, address.server.id, address.auth, address.key])
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
    insert into message (address, name, data)
    values (?, ?, ?)
    returning id
    """, [address_id, message.name, message.data])
    return inserted[0][0]

def get_message(address: Address, message_name):
    id, data, remote = query("""
    select id, data, remote_copy from message
    where address = ? and name = ?
    """, [address.id, message_name])
    return Message(id=id, name=message_name, data=data, address=address)

def remove_message(message: Message):
    query("""
    delete from message
    where id = ?
    """, [message.id])


# invites

# TODO: find a way to shorten this join
# (get db object by id ? require address ? iterate over messages ? use message@addr@host syntax ?)
# (for addr in list_addresses(): for message in list_messages():)
def list_invites():
    entries = query("""
    select
        invite.id,
        invite.room_name,
        invite.room_server,
        invite.room_auth,
        invite.room_key,

        message.name,
        address.name,
        server.url
    from invite

    join message
    on invite.message = message.id

    join address
    on message.address = address.id

    join server
    on address.server = server.id
    """)
    invites = []
    for (id, room_name, room_serv, room_auth, room_key, message_name, address_name, server_url) in entries:
        address = get_address(f"{address_name}@{server_url}")
        message = get_message(address, message_name)

        # TODO: get server if it exists (in case the server is trusted)
        server = Server(url=room_serv, trusted=False)
        room = Room(name=room_name, server=server, auth=room_auth, key=room_key)
        invites.append(Invite(id=id, room=room))

    return invites

def get_invite(message: Message):
    row = query("""
    select id, room_name, room_server, room_auth, room_key
    from invite
    where message = ?
    """, [message.id])[0]
    id, name, server, auth, key = row
    room = Room(name=name, server=Server(url=server), auth=auth, key=key)
    invite = Invite(
            id=id,
            room=room,
            )

    return invite

def remove_invite(message: Message):
    query("""
    delete from invite
    where message = ?
    """, [message.id])



# rooms

def list_rooms():
    rows = query("""
    select
        room.id,
        room.name,
        server.url,
        room.auth,
        room.sym_key
    from room
    join server
    on room.server = server.id
    """)
    rooms = []
    for (id, name, url, auth, key) in rows:
        room = Room(
            id=id,
            name=name,
            server=get_server(url),
            auth=auth,
            key=key,
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
        room.sym_key
    from room
    join server
    on room.server = server.id

    where room.name = ? and server.url = ?
    """, [name, server])
    if not result:
        return None
    (id, name, url, auth, key) = result[0]
    room = Room(
            id=id,
            name=name,
            server=get_server(url),
            auth=auth,
            key=key,
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
    insert into room (name, server, auth, sym_key)
    values (?, ?, ?, ?)
    returning id
    """, [room.name, room.server.id, room.auth, room.key])
    return inserted[0][0]

def remove_room(room: Room):
    query("""
    delete from room
    where id = ?
    """, [room.id])



# broadcasts

def list_broadcasts():
    rows = query("""
    select
        broadcast.id,
        broadcast.name,
        server.url,
        broadcast.auth,
        broadcast.auth_key,
        broadcast.access_key
    from broadcast
    join server
    on broadcast.server = server.id
    """)
    broadcasts = []
    for row in rows:
        (id, name, url, auth, auth_key, access_key) = row
        b = Broadcast(
            id=id,
            name=name,
            server=get_server(url),
            auth=auth,
            auth_key=auth_key,
            access_key=access_key,
        )
        broadcasts.append(b)
    return broadcasts

def get_broadcast(url):
    name, server = url.split("@")
    server = get_server(server)
    row = query("""
    select id, name, auth, auth_key, access_key
    from broadcast
    where name = ? and server = ?
    """, [name, server.id])[0]
    id, name, auth, authkey, accesskey = row
    return Broadcast(
            id = id,
            name = name,
            server = server,
            auth = auth,
            auth_key = authkey,
            access_key = accesskey,
            )

def add_broadcast(broadcast: Broadcast):
    existing = query("""
    select id from broadcast
    where name = ? and server = ?
    """, [broadcast.name, broadcast.server.id])
    if existing:
        return existing[0][0]

    inserted = query("""
    insert into broadcast (name, server, auth, auth_key, access_key)
    values (?, ?, ?, ?, ?)
    returning id
    """, [broadcast.name, broadcast.server.id, broadcast.auth, broadcast.auth_key, broadcast.access_key])
    return inserted[0][0]

def remove_broadcast(broadcast: Broadcast):
    query("""
    delete from broadcast
    where id = ?
    """, [broadcast.id])

