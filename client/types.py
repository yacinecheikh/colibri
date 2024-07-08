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

@dataclass
class Room:
    name: str
    server: str
    auth: str
    key: str  # symetric key

    def __str__(self):
        return f"{self.name}@{self.server}"

