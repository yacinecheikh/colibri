from dataclasses import dataclass
from typing import Union


@dataclass
class Address:
    name: str
    server: str
    auth: Union[str, None]
    key: str  # name of the pub/private key files in data/keys/

    def __str__(self):
        return f"{self.name}@{self.server}"

    def __repr__(self):
        return str(self)

@dataclass
class Room:
    name: str
    server: str
    auth: str
    key: str  # symetric key
    data_file: str

    def __str__(self):
        return f"{self.name}@{self.server}"

    def __repr__(self):
        return str(self)


# server is just a url
# message ?
# invite
@dataclass
class Invite:
    # Room invitation
    name: str
    server: str
    auth: str
    key: str

@dataclass
class Message:
    name: str
    server: str
    data: str
