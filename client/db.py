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
    return query("""
    select url from server
    """)

def list_invites():
    return query("""
    select * from invite
    """)
    
def list_stores():
    return query("""
    select store.address, server.url
    from store
    join server
    on store.server = server.id
    """)

def list_addresses():
    return query("""
    select message_address.address, server.url
    from message_address
    join server
    on message_address.server = server.id
    """)




def add_server(address):
    query("""
    insert into server (url)
    values (?)
    """, [address])

def add_store(address, server, auth, aes_key):
    return query("""
    insert into store (address, server, auth, aes_key)
    values (?,
        (select id from server
        where url = ?),
        ?, ?)
    """, [address, server, auth, aes_key])

def add_address(address, server, key_name):
    pass

#def add_invite(a





def get_store(address, server):
    return query("""
    select store.*
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

