import requests

def post(endpoint, data):
    return requests.post(endpoint, json=data).json()


def register_store(server, auth):
    address = post(f'{server}/address/register', {
        'auth': auth,
    })
    return address

def register_message_address(server):
    pass

def read_store(address, server, auth):
    pass

def write_store(address, server, auth):
    pass

def read_messages(address, server, auth):
    pass


def delete_message_cache(address, server, auth):
    pass

