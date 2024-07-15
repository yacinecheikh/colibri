import db
from hashlib import sha256
from base64 import b64encode, b64decode

def sha(x):
    h = sha256()
    h.update(x.encode())
    return b64encode(h.digest())

addr = db.add_address('password')
print(addr)

print(db.get_messages(addr, 'password'))

msg = db.add_message(addr, 'hi')

print(db.get_messages(addr, 'password'))

print(db.remove_message(addr, msg, 'password'))


addr = db.add_store('pw')

# default store content is ""
print(db.get_store(addr, 'pw'))

print(db.set_store(addr, 'pw', '<stored data>', sha("")))
print(db.get_store(addr, 'pw'))
