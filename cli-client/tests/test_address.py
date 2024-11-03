import pytest

from libtest import run, create_profile, create_minimal_profile


@pytest.mark.net
def test_address_management():
    create_profile("addresses")

    assert run("addresses", "list-owned-addresses") == ""
    assert run("addresses", "list-foreign-addresses") == ""

    # generate and remove addresses
    name = run("addresses", "new-address") # " http://localhost:8000"
    assert name.endswith("\n")
    name = name[:-1]
    assert run("addresses", "list-owned-addresses") == f"{name}\n"
    assert run("addresses", "list-foreign-addresses") == f""
    assert run("addresses", f"remove-address {name}") == "ok\n"
    assert run("addresses", "list-owned-addresses") == ""
    assert run("addresses", "list-foreign-addresses") == ""

    server = run("addresses", "list-trusted-servers")[:-1]
    address = run("addresses", f"new-address {server}")[:-1]

    # export, remove and import
    exported = run("addresses", f"export-address {address}")
    # TODO: document how the output is "ok" instead of using the return codes
    assert run("addresses", f"remove-address {address}") == "ok\n"
    # make sure everything is clean
    assert run("addresses", "list-owned-addresses") == ""
    assert run("addresses", "list-foreign-addresses") == ""
    assert run("addresses", "import-address", exported) == "ok\n"
    assert run("addresses", "list-owned-addresses") == f"{address}\n"
    assert run("addresses", "list-foreign-addresses") == ""
    # assert export gives the same output as before
    # this confirms exporting/importing a key gives the exact same state
    assert run("addresses", f"export-address {address}") == exported

    # export public info, remove and import
    exported = run("addresses", f"export-address-info {address}")
    assert run("addresses", f"remove-address {address}") == "ok\n"
    # TODO: remove assert == "ok\n" tests (run() already asserts that the return code is 0)
    assert run("addresses", f"import-address", exported) == "ok\n"
    assert run("addresses", "list-owned-addresses") == ""
    assert run("addresses", "list-foreign-addresses") == f"{address}\n"


@pytest.mark.net
def test_message_sending():
    create_profile("sender")
    create_profile("receiver")

    sender_address = run("sender", "new-address")[:-1]
    receiver_address = run("receiver", "new-address")[:-1]

    # basic health check
    assert run("sender", "list-foreign-addresses") == ""
    assert run("receiver", "list-foreign-addresses") == ""
    assert run("sender", f"list-messages {sender_address}") == ""
    assert run("receiver", f"list-messages {receiver_address}") == ""

    # export receiver's contact address
    receiver_address_info = run("receiver", f"export-address-info {receiver_address}")
    assert run("sender", f"import-address", receiver_address_info) == "ok\n"

    assert run("sender", "list-foreign-addresses") == f"{receiver_address}\n"

    # send a message
    assert run("sender", f"send-message {receiver_address}", "hi there") == "ok\n"
    assert run("receiver", f"list-messages {receiver_address}") == ""
    assert run("receiver", f"fetch-messages {receiver_address}") == "ok\n"
    output = run("receiver", f"list-messages {receiver_address}")
    messages = output[:-1].split("\n")
    print("found messages:", messages)
    assert len(messages) == 1
    message = messages[0]
    assert run("receiver", f"read-message {message}") == "hi there\n"


    assert run("receiver", f"remove-message {message}") == "ok\n"
    assert run("receiver", f"list-messages {receiver_address}") == ""
    # the message is still on the remote server, and can be downloaded again
    assert run("receiver", f"fetch-messages {receiver_address}") == "ok\n"
    assert run("receiver", f"list-messages {receiver_address}") == output
    assert run("receiver", f"list-remote-messages {receiver_address}") == output

    message_name = message.split("@")[0]
    assert run("receiver", f"remove-remote-messages {receiver_address} {message_name}") == "ok\n"
    assert run("receiver", f"list-remote-messages {receiver_address}") == ""

#@pytest.mark.net
#def test_message_management():
#    # TODO: fetch, delete, fetch again, delete remove,...
#    assert False

