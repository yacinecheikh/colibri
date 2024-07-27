from libtest import debug, info, run, create_profile


create_profile("sender")
create_profile("receiver")

#room = run("sender", "new-room")[:-1]
addr = run("receiver", "new-address")[:-1]
exported = run("receiver", f"show-address {addr}")
run("sender", "add-foreign-address", exported)
run("sender", "list-foreign-addresses")
run("sender", f"send-message {addr}", "test")
run("receiver", f"fetch-messages {addr}")
message = run("receiver", f"list-messages {addr}")[:-1]
run("receiver", f"read-message {message}")
run("receiver", f"list-messages {addr}")
run("receiver", f"list-remote-messages {addr}")
message_name = message.split("@", 1)[0]
run("receiver", f"remove-message {addr} {message_name}")
run("receiver", f"list-messages {addr}")
run("receiver", f"list-remote-messages {addr}")
run("receiver", f"fetch-messages {addr}")
run("receiver", f"list-messages {addr}")
run("receiver", f"list-remote-messages {addr}")
run("receiver", f"remove-remote-messages {addr} {message_name}")
run("receiver", f"list-messages {addr}")
run("receiver", f"list-remote-messages {addr}")
# TODO: remove-message, remove-remote-message

