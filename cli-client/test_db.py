import db
from datatypes import Server, Address, Room, Broadcast
from crypto_module import AddressKeys, RoomKeys, BroadcastKeys
from uuid import uuid4 as uuid
import random


# mock the database
import os
if os.path.exists("tests.sqlite3"):
    os.remove("tests.sqlite3")
import sqlite3
db.db = sqlite3.connect("tests.sqlite3")
# initialize table structures
with open("init.sql") as f:
    db.db.executescript(f.read())

def test_servers():
    print("servers:")
    assert len(db.list_servers()) == 0
    print(db.add_server(Server("http://localhost:8000")))
    print(db.add_server(Server("http://localhost:8000")))
    print(db.list_servers())
    assert len(db.list_servers()) == 1


    server = random.choice(db.list_servers())
    assert server.trusted == False


def test_addresses():
    assert len(db.list_addresses()) == 0

    address = Address(
            name=str(uuid()),
            server=db.list_servers()[0],
            auth=str(uuid()),
            keys=AddressKeys(),  # mock; tests will run as long as no crypto feature is used
            )
    db.add_address(address)

    assert len(db.list_addresses()) == 1

    assert db.get_address(str(address)) is not None


def test_rooms():
    assert len(db.list_rooms()) == 0
    room = Room(
            name=str(uuid()),
            server=db.list_servers()[0],
            auth=str(uuid()),
            keys=RoomKeys(),
            )
    db.add_room(room)
    assert len(db.list_rooms()) == 1
    assert db.get_room(str(room)) is not None


def test_broadcasts():
    assert len(db.list_broadcasts()) == 0
    broadcast = Broadcast(
            name=str(uuid()),
            server=db.list_servers()[0],
            auth=str(uuid()),
            keys=BroadcastKeys(),
            )
    db.add_broadcast(broadcast)
    assert len(db.list_broadcasts()) == 1
    assert db.get_broadcast(str(broadcast)) is not None

