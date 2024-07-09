import sqlite3
#import os
from uuid import uuid4 as uuid

db = sqlite3.connect('storage.db', check_same_thread=False)

#"""
#sql additions
#"""
#
#import uuid
#def gen_id():
#    return str(uuid.uuid4())
#
#db.create_function('uuid', 0, gen_id)


"""
create tables


-ignore primary/foreign keys constraints
-always use uuid as id (to prevent chronological correlation)
-hashing is not needed because the generated passwords only unlock encrypted data (simple spam prevention)
"""

db.executescript("""
create table if not exists message (
    id text primary key,
    address text,
    data text
) without rowid;

create table if not exists address (
    uuid text primary key,
    auth text
) without rowid;

create table if not exists store (
    uuid text primary key,
    auth text,
    data text
) without rowid
""")

db.commit()

def add_address(auth):
    # create a free address id
    while True:
        # address uuid
        address = str(uuid())
        result = db.execute("""
        select uuid from address
        where uuid = ?
        """, [address]).fetchone()
        if result is None:
            break
    db.execute("""
    insert into address (uuid, auth)
    values (?, ?)
    """, [address, auth])
    db.commit()
    return address

#def test_address(address):
#    # exists ?
#    pass

def get_messages(address, auth):
    # will return nothing with the wrong password
    result = db.execute("""
    select message.id, message.data
    from message
    join address
    on message.address = address.uuid
    where address.uuid = ?
    and address.auth = ?
    """, (address, auth))
    return result.fetchall()
    messages = []
    for (mid, mdata) in result.fetchall():
        messages.append({
            'id': mid,
            'data': mdata,
        })
    return messages

def add_message(address, data):
    # create a free message id
    # TODO: message ids should be specific to the address
    # (primary key = (address, id))
    while True:
        identifier = str(uuid())
        res = db.execute("""
        select id from message
        where id = ?
        """, [identifier])
        if res.fetchone() is None:
            break
    db.execute('''
    insert into message (id, address, data)
    values (?, ?, ?)
    ''', (identifier, address, data))
    db.commit()
    return identifier

# TODO: return True if succeeded
def remove_message(address, message_id, auth):
    # delete with join deletes everything joined
    # (cannot join with the address)
    db.execute("""
    delete from message
    where id not in (
        select id
        from message
        join address
        on message.address = address.uuid
        where address.uuid = ?
          and address.auth = ?
    )
    """, (address, auth))
    db.commit()

#def test_store(address):
#    pass


def add_store(auth):
    # create a free store id
    while True:
        store_id = str(uuid())
        result = db.execute("""
        select uuid from store
        where uuid = ?
        """, [store_id]).fetchone()
        if result is None:
            break
    db.execute("""
    insert into store (uuid, auth, data)
    values (?, ?, '')
    """, [store_id, auth])
    db.commit()
    return store_id


def get_store(store_id, auth):
    res = db.execute("""
    select data from store
    where uuid = ?
      and auth = ?
    """, (store_id, auth)).fetchone()
    # None -> fail
    if res:
        return res[0]

def set_store(store_id, auth, data):
    # TODO: return True if success
    # TODO: add hashing to prevent collisions and allow clients to synchronize
    db.execute("""
    update store
    set data = ?
    where uuid = ?
      and auth = ?
    """, (data, store_id, auth))
    db.commit()

