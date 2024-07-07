import sqlite3

db = sqlite3.connect("data/db.sqlite3")

# initialize table structures
with open("init.sql") as f:
    db.executescript(f.read())

def query(*args):
    "wrapper over sqlite connection methods"
    cursor = db.execute(*args)
    db.commit()
    return cursor.fetchall()


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
    return query("""
    select room.name || '@' || server.url
    from room
    join server
    on room.server = server.id
    """)

def list_addresses():
    return query("""
    select address.name, server.url
    from address
    join server
    on address.server = server.id
    """)

# TODO: là là ici là
def list_invites():
    pass

# get

def get_server(url):
    server = query("""
    select * from server
    where url = ?
    """, [url])[0]
    return {
        "id": server[0],
        "url": server[1],
    }

def get_room(name, server):
    room = query("""
    select
        room.id,
        room.auth,
        room.sym_key,
        room.data_file
    from room
    join server
    on room.server = server.id

    where room.name = ? and server.url = ?
    """, [name, server])[0]
    # TODO:
    return {
        "id": room[0],
        "name": name,
        "server": server,
        "auth": room[1],
        "sym_key": room[2],
        "data_file": room[3],
    }

def get_address(name, server):
    address = query("""
    select
        address.id,
        address.auth,
        address.key_name
    from address
    join server
    on address.server = server.id

    where address.name = ? and server.url = ?
    """, [name, server])[0]
    return {
        "id": address[0],
        "name": name,
        "server": server,
        "auth": address[1],
        "key_name": address[2],
    }



# add

def add_server(url):
    query("""
    insert into server (url)
    values (?)
    """, [url])

def add_room(name, server, auth, sym_key, data_file):
    server_id = get_server(server)["id"]

    query("""
    insert into room (name, server, auth, sym_key, data_file)
    values (?, ?, ?, ?, ?)
    """, [name, server_id, auth, sym_key, data_file])

def add_address(name, server, auth, key_name):
    if server not in list_servers():
        add_server(server)
    server_id = get_server(server)["id"]
    query("""
    insert into address (name, server, auth, key_name)
    values (?, ?, ?, ?)
    """, [name, server_id, auth, key_name])


# TODO: là là ici là

#def add_invite(a








def remove_invite(invite_id):
    return query("""
    delete from invite
    where id = ?
    """, [invite_id])

