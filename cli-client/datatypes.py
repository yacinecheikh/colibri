from dataclasses import dataclass
from typing import Union

from crypto_module import AddressKeys, RoomKeys, BroadcastKeys

# DB objects are first created without an id before being saved to the database
Id = Union[int, None]


# database objects
@dataclass
class Server:
    url: str
    trusted: bool = False
    id: Id = None

    def __repr__(self):
        return self.url

    def __eq__(self, other):
        return self.url == other.url

@dataclass
class Address:
    name: str
    server: Server
    auth: Union[str, None]
    keys: AddressKeys
    id: Id = None

    def __str__(self):
        return f"{self.name}@{self.server}"

    def __repr__(self):
        return str(self)

@dataclass
class Room:
    name: str
    server: Server
    auth: str

    keys: RoomKeys
    last_hash: Union[str, None] = None

    id: Id = None

    def __str__(self):
        return f"{self.name}@{self.server}"

    def __repr__(self):
        return str(self)


@dataclass
class Broadcast:
    name: str
    server: Server
    auth: str
    keys: BroadcastKeys
    id: Id = None

    def __repr__(self):
        return f"{self.name}@{self.server}"


@dataclass
class Message:
    name: str
    # the full Address has to be known in order to decode messages
    address: Address
    data: str
    remote: bool  # remote copy
    id: Id = None

    def __repr__(self):
        return f"{self.name}@{self.address}"



# room/broadcast/address info are embedded in special message types
# these objects are stored in messages

@dataclass
class RoomInfo:
    id: Id = None
    message: Message
    url: str
    auth: str
    keys: str

@dataclass
class AddressInfo:
    id: Id = None
    message: Message
    url: str
    keys: str

@dataclass
class BroadcastInfo
    id: Id = None
    message: Message
    url: str
    keys: str

