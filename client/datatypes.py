from dataclasses import dataclass
from typing import Union


# DB objects are first created without an id before being saved to the database
Id = Union[int, None]


# filesystem object (useless since there is not enough data to justify a wrapper class)
#@dataclass
#class KeyPair:
#    name: str

#@dataclass
#class Key:
#    key: str


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
    key: str  # asymetric key (stored in data/keys)
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
    key: str  # symetric key
    #data_file: str
    id: Id = None

    def __str__(self):
        return f"{self.name}@{self.server}"

    def __repr__(self):
        return str(self)



@dataclass
class Message:
    name: str
    # the full Address has to be known in order to decode messages
    address: Address
    data: str
    id: Id = None

    def __repr__(self):
        return f"{self.name}@{self.address}"


# invites are messages with the credentials to access a Room
@dataclass
class Invite:
    # an invite is independant from the message that delivered the invite (a unique invite can be sent with multiple messages, and an invite can exist after its message has been removed)
    #message: Message
    room: Room
    id: Id = None


@dataclass
class Broadcast:
    name: str
    server: Server
    auth: str
    auth_key: str  # asymetric signing key
    access_key: str  # symetric key
    id: Id = None

