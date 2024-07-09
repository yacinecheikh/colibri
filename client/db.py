import sqlite3

from datatypes import Room, Address


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

# read

def list_servers():
    servers = query("""
    select url from server
    """)
    return [server[0] for server in servers]

def list_rooms():
    rooms = query("""
    select
        room.name,
        server.url,
        room.auth,
        room.sym_key,
        room.data_file
    from room
    join server
    on room.server = server.id
    """)
    rooms = [Room(*room) for room in rooms]
    return rooms

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
    return addresses

# TODO:
def list_invites():
    pass

# get

def get_room(url):
    name, server = url.split('@')
    room = query("""
    select
        room.name,
        server.url,
        room.auth,
        room.sym_key,
        room.data_file
    from room
    join server
    on room.server = server.id

    where room.name = ? and server.url = ?
    """, [name, server])[0]
    return Room(*room)

# TODO: add bounds checks
def get_address(url):
    name, server = url.split('@')
    address = query("""
    select
        address.name,
        server.url,
        address.auth,
        address.key_name
    from address
    join server
    on address.server = server.id

    where address.name = ? and server.url = ?
    """, [name, server])[0]
    return Address(*address)



# add

# add if not already present and return id
def add_server(url):
    existing = query("""
    select id
    from server
    where url = ?
    """, [url])
    if existing:
        return existing[0][0]

    inserted = query("""
    insert into server (url)
    values (?)
    returning id
    """, [url])
    return inserted[0][0]

def add_room(room):
    server_id = add_server(room.server)
    existing = query("""
    select id
    from room
    where name = ? and server = ?
    """, [room.name, server_id])
    if existing:
        return existing[0][0]
    inserted = query("""
    insert into room (name, server, auth, sym_key, data_file)
    values (?, ?, ?, ?, ?)
    returning id
    """, [room.name, server_id, room.auth, room.key, room.data_file])
    return inserted[0][0]

def add_address(address):
    server_id = add_server(address.server)
    # safety check before inserting
    # + return the id for further foreign key insertions
    existing = query("""
    select id
    from address
    where name = ? and server = ?
    """, [address.name, server_id])
    if existing:
        return existing[0][0]

    inserted = query("""
    insert into address (name, server, auth, key_name)
    values (?, ?, ?, ?)
    returning id
    """, [address.name, server_id, address.auth, address.key])
    return inserted[0][0]

def add_message(message):
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

# TODO:

#def add_invite(a


def remove_invite(invite_id):
    return query("""
    delete from invite
    where id = ?
    """, [invite_id])

