from uuid import uuid4 as uuid

import net


serv = "http://localhost:8000"

print(net.register_room(serv, str(uuid())))
print(net.register_address(serv, str(uuid())))
