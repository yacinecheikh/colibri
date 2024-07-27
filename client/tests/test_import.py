from libtest import debug, info, run, create_profile


create_profile("sender")
create_profile("receiver")

room = run("sender", "new-room")[:-1]
addr = run("receiver", "new-address")[:-1]
exported = run("receiver", f"export-address {addr}")
run("sender", "import-address", exported)
