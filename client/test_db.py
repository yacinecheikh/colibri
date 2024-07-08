import db
from datatypes import Address, Room
from uuid import uuid4 as uuid
import random


print("servers:")
print(db.list_servers())
print(db.add_server("http://localhost:8000"))
print(db.add_server("http://localhost:8000"))
print(db.list_servers())


server = random.choice(db.list_servers())
print("using server", server)


print("addresses:")
print(db.list_addresses())

address = Address(
        name=str(uuid()),
        server=server,
        auth=str(uuid()),
        key=str(uuid())
        )
db.add_address(address)

print(db.list_addresses())
found = db.get_address(str(address))
print(found)



print("rooms:")
print(db.list_rooms())
room = Room(
        name=str(uuid()),
        server=server,
        auth=str(uuid()),
        key=str(uuid()),
        data_file=str(uuid())
        )
db.add_room(room)
print(db.list_rooms())
print(db.get_room(str(room)))
