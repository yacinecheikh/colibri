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
/address:
    /register: post (auth) -> addr
    /{addr}: get (auth) -> [(id, data)]
    /{addr}: post (data) -> ok
    /{addr}: delete (auth, [id]) -> [ok]
/store:
    /register: post (auth) -> addr
    /{addr}: get (auth) -> data
    /{addr}: post (auth, data, hash) -> ok
"""

@app.post('/address/register')
def address_register(req: Auth):
    return db.add_address(req.auth)

@app.get('/address/{uuid}')
def read_address(uuid: str, req: Auth):
    messages = db.get_messages(uuid, req.auth)
    result = []
    for (mid, mdata) in messages:
        result.append({
            'id': mid,
            'data': mdata,
        })
    return result

@app.post('/address/{uuid}')
def send_message(uuid: str, req: Data):
    db.add_message(uuid, req.data)
    # TODO: return ok unless internal error
    return "ok"

@app.delete('/address/{uuid}')
def remove_messages(uuid: str, req: MessageDelete):
    for message in req.ids:
        db.remove_message(uuid, message, req.auth)
    # TODO: status ?
    return 'ok'


@app.post('/store/register')
def store_register(req: Auth):
    return db.add_store(req.auth)

@app.get('/store/{uuid}')
def get_store(uuid: str, req: Auth):
    return db.get_store(uuid, req.auth)

@app.post('/store/{uuid}')
def set_store(uuid: str, req: Write):
    return db.set_store(uuid, req.auth, req.data)


