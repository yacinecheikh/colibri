import sqlite3
#import os
from uuid import uuid4 as uuid

db = sqlite3.connect('db.db', check_same_thread=False)

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
-- 1 message_queue - many message
create table if not exists message (
    id text primary key,
    address text,
    data text
) without rowid;

create table if not exists message_queue (
    address text primary key,
    auth text
) without rowid;

create table if not exists store (
    address text primary key,
    auth text,
    data text
) without rowid
""")

db.commit()

def add_address(auth):
    # create a free address
    while True:
        address = str(uuid())
        result = db.execute("""
        select address from message_queue
        where address = ?
        """, [address]).fetchone()
        if result is None:
            break
    db.execute("""
    insert into message_queue (address, auth)
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
    join message_queue
    on message.address = message_queue.address
    where message_queue.address = ?
    and message_queue.auth = ?
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
    # create a free address
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
    # (cannot join with the message_queue)
    db.execute("""
    delete from message
    where id not in (
        select id
        from message
        join message_queue
        on message.address = message_queue.address
        where message_queue.address = ?
          and message_queue.auth = ?
    )
    """, (address, auth))
    db.commit()

#def test_store(address):
#    pass


def add_store(auth):
    # create a free address
    while True:
        address = str(uuid())
        result = db.execute("""
        select address from store
        where address = ?
        """, [address]).fetchone()
        if result is None:
            break
    db.execute("""
    insert into store (address, auth, data)
    values (?, ?, '')
    """, [address, auth])
    db.commit()
    return address


def get_store(address, auth):
    res = db.execute("""
    select data from store
    where address = ?
      and auth = ?
    """, (address, auth)).fetchone()
    # None -> fail
    if res:
        return res[0]

def set_store(address, auth, data):
    # TODO: return True if success
    # TODO: add hashing to prevent collisions and allow clients to synchronize
    db.execute("""
    update store
    set data = ?
    where address = ?
      and auth = ?
    """, (data, address, auth))
    db.commit()

