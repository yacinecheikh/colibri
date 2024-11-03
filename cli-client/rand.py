from uuid import uuid4 as uuid


def auth():
    return str(uuid())
