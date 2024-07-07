import requests

def post(endpoint, data):
    return requests.post(endpoint, json=data).json()
def get(endpoint, data):
    return requests.get(endpoint, json=data).json()


def register_store(server, auth):
    store = post(f'{server}/store/register', {
        'auth': auth,
    })
    return store

def register_address(server, auth):
    address = post(f'{server}/address/register', {
        'auth': auth,
    })
    return address

# TODO: test
def read_store(store, server, auth):
    return get(f"{server}/store/{store}", {
        "auth": auth,
    })

def write_store(address, server, auth, data):
    return post(f"{server}/address/{address}", {
        "auth": auth,
        "data": data,
    })

def read_messages(address, server, auth):
    return get(f"{server}/address/{address}", {
        "auth": auth,
    })


def delete_message_cache(address, server, auth):
    pass

