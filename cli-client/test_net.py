import pytest

from uuid import uuid4 as uuid
from hashlib import sha256

from datatypes import Server, Address, Room, Broadcast
import net

serv = Server("http://localhost:8000")


@pytest.mark.net
def test_rooms():
    auth = str(uuid())
    name = net.register_room(serv, auth)
    room = Room(
            name=name,
            server=serv,
            auth=auth,
            keys=None,
            )
    read = net.read_room(room)
    assert read == ""

    h = sha256()
    h.update(read.encode())
    room.last_hash = h.hexdigest()

    assert net.write_room(room, "test") == True
    assert net.read_room(room) == "test"


@pytest.mark.net
def test_broadcasts():
    auth = str(uuid())
    name = net.register_broadcast(serv, auth)
    broadcast = Broadcast(
            name=name,
            server=serv,
            auth=auth,
            keys=None,
            )
    read = net.read_broadcast(broadcast)
    assert read == ""

    assert net.write_broadcast(broadcast, "test") == "ok"
    assert net.read_broadcast(broadcast) == "test"


@pytest.mark.net
def test_addresses():
    auth = str(uuid())
    name = net.register_address(serv, auth)
    address = Address(
            name=name,
            server=serv,
            auth=auth,
            keys=None,
            )
    messages = net.read_messages(address)
    assert len(messages) == 0

    assert net.send_message(address, "test") == "ok"

    messages = net.read_messages(address)
    assert len(messages) == 1
    message = messages[0]

    assert message.data == "test"

    assert net.delete_messages(address, [message.name]) == "ok"

    assert len(net.read_messages(address)) == 0

