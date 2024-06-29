# from typing import Union
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
import db


app = FastAPI()


class Auth(BaseModel):
    auth: str

class Data(BaseModel):
    data: str

class MessageDelete(Auth):
    message_ids: List[str]

class Write(Auth, Data):
    pass




"""
/message:
    /register: post (auth) -> addr
    /{addr}: get (auth) -> [(id, data)]
    /{addr}: post (data) -> ok
    /{addr}: delete (auth, [id]) -> [ok]
        used to clear leftover data
/store:
    /create: post (auth) -> addr
    /{addr}: get (auth) -> data
    /{addr}: post (auth, data, hash) -> ok

"""

@app.post('/message/register')
def message_register(req: Auth):
    return db.add_address(req.auth)

@app.get('/message/{address}')
def read_mails(address: str, req: Auth):
    messages = db.get_messages(address, req.auth)
    result = []
    for (mid, mdata) in messages:
        result.append({
            'id': mid,
            'data': mdata,
        })
    return result

@app.post('/message/{address}')
def send_message(address: str, req: Data):
    db.add_message(address, req.data)
    # TODO: return ok unless internal error
    return []

@app.delete('/message/{address}')
def remove_messages(address: str, req: MessageDelete):
    for message in req.ids:
        db.remove_message(address, message, req.auth)
    # TODO: status ?
    return 'ok'


@app.post('/store/register')
def store_register(req: Auth):
    return db.add_store(req.auth)

@app.get('/store/{address}')
def get_store(address: str, req: Auth):
    return db.get_store(address, req.auth)

@app.post('/store/{address}')
def set_store(address: str, req: Write):
    return db.set_store(address, req.auth, req.data)


