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

def list_servers():
    servers = query("""
    select url from server
    """)
    return [server[0] for server in servers]

def list_invites():
    return query("""
    select * from invite
    """)
    
def list_stores():
    return query("""
    select store.name, server.url
    from store
    join server
    on store.server = server.id
    """)

def list_addresses():
    return query("""
    select address.name, server.url
    from address
    join server
    on address.server = server.id
    """)




def add_server(url):
    query("""
    insert into server (url)
    values (?)
    """, [url])

def add_store(name, server, auth, aes_key, data_dir):
    return query("""
    insert into store (name, server, auth, aes_key, data_dir)
    values (?,
        (select id from server
        where url = ?),
        ?, ?, ?)
    """, [name, server, auth, aes_key, data_dir])

def add_address(name, server, auth, key_name):
    if server not in list_servers():
        add_server(server)
    return query("""
    insert into address (name, server, auth, key_name)
    values (?,
        (select id from server
        where url = ?),
        ?, ?)
    """, [name, server, auth, key_name])

#def add_invite(a








def get_address(name, server):
    return query("""
    select address.name, address.auth, address.key_name, server.url
    from address
    join server
    on server.id = address.server

    where address.name = ? and server.url = ?
    """, [name, server])[0]


def get_store(address, server):
    return query("""
    select store.*, server.url
    from store
    join server
    on store.server = server.id

    where store.address = ? and server.url = ?
    """, [address, server])[0]


def get_message_address(address, server):
    ("""
    select query.*
    """)
    pass

def remove_invite(invite_id):
    return query("""
    delete from invite
    where id = ?
    """, [invite_id])

