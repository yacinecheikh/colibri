import pytest

from libtest import run, create_profile, create_minimal_profile


@pytest.mark.net
def test_room_management():
    create_profile("rooms")

    assert run("rooms", "list-rooms") == ""

    # generate and remove rooms
    name = run("rooms", "new-room") # " http://localhost:8000"
    assert name.endswith("\n")
    name = name[:-1]
    assert run("rooms", "list-rooms") == f"{name}\n"
    assert run("rooms", f"remove-room {name}") == "ok\n"
    assert run("rooms", "list-rooms") == ""

    server = run("rooms", "list-trusted-servers")[:-1]
    room = run("rooms", f"new-room {server}")[:-1]

    # export and import room access
    exported = run("rooms", f"export-room {room}")
    run("rooms", f"remove-room {room}")
    assert run("rooms", "list-rooms") == ""
    assert run("rooms", "import-room", exported) == "ok\n"
    # assert room export gives the same output as before
    assert run("rooms", f"export-room {room}") == exported


@pytest.mark.net
def test_room_rw():
    create_profile("room-member-1")
    create_profile("room-member-2")

    room = run("room-member-1", "new-room")[:-1]
    room_access = run("room-member-1", f"export-room {room}")
    run("room-member-2", "import-room", room_access)

    # read and write room-member-1
    assert run("room-member-1", f"read-room {room}") == ""
    assert run("room-member-1", f"write-room {room}", "hi there") == "ok\n"
    assert run("room-member-1", f"read-room {room}") == "hi there\n"

    # read and write room-member-2
    assert run("room-member-2", f"read-room {room}") == "hi there\n"
    assert run("room-member-2", f"write-room {room}", "hi") == "ok\n"
    assert run("room-member-2", f"read-room {room}") == "hi\n"
    assert run("room-member-1", f"read-room {room}") == "hi\n"

