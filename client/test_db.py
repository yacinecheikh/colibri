import db

print("servers:")
print(db.list_servers())
print(db.add_server("http://localhost:8000"))
print(db.add_server("http://localhost:8000"))
print(db.list_servers())

# TODO: rewrite the tests
import sys
sys.exit()

print("addresses:")

print(db.list_addresses())
db.add_address("addr", "http://localhost:8000", "auth", "key_name")
print(db.list_addresses())
print(db.get_address("addr", "http://localhost:8000"))


print("rooms:")
print(db.list_rooms())
db.add_room("room", "http://localhost:8000", "auth", "sym_key", "key-data-file")
print(db.list_rooms())
print(db.get_room("room", "http://localhost:8000"))
