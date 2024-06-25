import requests
from uuid import uuid4 as uuid


url = 'http://localhost:8000'
headers = {
        'Content-Type': 'application/json',
}

#def query(method, endpoint, data):
#    endpoint = f'{url}/{endpoint}'

def get(endpoint, data={}):
    print(f'GET {url}/{endpoint}')
    print(data)
    #response = requests.get(f'{url}/{endpoint}', params=data)
    response = requests.get(f'{url}/{endpoint}', json=data)

    print(response.status_code)
    print(response.json())  
    return response.json()

def post(endpoint, data={}):
    print(f'POST {url}/{endpoint}')
    print(data)
    response = requests.post(f'{url}/{endpoint}', headers=headers, json=data)

    print(response.status_code)
    print(response.json())  
    return response.json()



"""
message
"""

message_auth = str(uuid())

post('message/register')
message_address = post('/message/register', {
    'auth': message_auth,
})

get(f'message/{message_address}', {
    'auth': message_auth,
})

post(f'message/{message_address}', {
    'data': 'hi',
})

messages = get(f'message/{message_address}', {
    'auth': message_auth,
})

ids = [message['id'] for message in messages]



"""
store
"""

store_auth = str(uuid())

post('store/register')

store_address = post('store/register', {
    'auth': store_auth,
})

get(f'store/{store_address}')
get(f'store/{store_address}', {
    'auth': store_auth,
})

post(f'store/{store_address}')
post(f'store/{store_address}', {
    'auth': store_auth,
    'data': 'storage',
})

get(f'store/{store_address}', {
    'auth': store_auth,
})

