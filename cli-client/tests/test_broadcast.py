import pytest

from libtest import run, create_profile, create_minimal_profile


@pytest.mark.net
def test_broadcast_management():
    create_profile("broadcasts")

    assert run("broadcasts", "list-foreign-broadcasts") == ""
    assert run("broadcasts", "list-owned-broadcasts") == ""

    # generate and remove broadcasts
    name = run("broadcasts", "new-broadcast") # " http://localhost:8000"
    assert name.endswith("\n")
    name = name[:-1]
    assert run("broadcasts", "list-owned-broadcasts") == f"{name}\n"
    assert run("broadcasts", "list-foreign-broadcasts") == ""
    assert run("broadcasts", f"remove-broadcast {name}") == "ok\n"
    assert run("broadcasts", "list-owned-broadcasts") == ""
    assert run("broadcasts", "list-foreign-broadcasts") == ""

    server = run("broadcasts", "list-trusted-servers")[:-1]
    broadcast = run("broadcasts", f"new-broadcast {server}")[:-1]

    # export and import private keys
    exported = run("broadcasts", f"export-broadcast {broadcast}")
    run("broadcasts", f"remove-broadcast {broadcast}")
    assert run("broadcasts", "list-owned-broadcasts") == ""
    assert run("broadcasts", "list-foreign-broadcasts") == ""
    #assert run("broadcasts", "import-broadcast", exported) == "ok\n"
    run("broadcasts", "import-broadcast", exported)
    assert run("broadcasts", "list-owned-broadcasts") == f"{broadcast}\n"
    assert run("broadcasts", "list-foreign-broadcasts") == ""
    # assert export gives the same output as before
    assert run("broadcasts", f"export-broadcast {broadcast}") == exported


    # export and import public (view) info
    exported = run("broadcasts", f"export-broadcast-info {broadcast}")
    assert run("broadcasts", f"remove-broadcast {broadcast}") == "ok\n"
    assert run("broadcasts", "import-broadcast", exported) == "ok\n"
    assert run("broadcasts", "list-owned-broadcasts") == ""
    assert run("broadcasts", "list-foreign-broadcasts") == f"{broadcast}\n"


@pytest.mark.net
def test_broadcast_rw():
    create_profile("broadcast-writer")
    create_profile("broadcast-viewer")

    broadcast = run("broadcast-writer", "new-broadcast")

    broadcast_view = run("broadcast-writer", f"export-broadcast-info {broadcast}")
    run("broadcast-viewer", "import-broadcast", broadcast_view)

    # read and write broadcast-writer
    assert run("broadcast-writer", f"read-broadcast {broadcast}") == ""
    assert run("broadcast-writer", f"write-broadcast {broadcast}", "hi there") == "ok\n"
    assert run("broadcast-writer", f"read-broadcast {broadcast}") == "hi there\n"

    assert run("broadcast-viewer", f"read-broadcast {broadcast}") == "hi there\n"


    # TODO: verify that the viewer cannot write

