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



@dataclass
class Message:
    name: str
    # the full Address has to be known in order to decode messages
    address: Address
    data: str

    def __repr__(self):
        return f"{self.name}@{self.address}"
