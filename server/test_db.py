import db

addr = db.add_address('password')
print(addr)

print(db.get_messages(addr, 'password'))

msg = db.add_message(addr, 'hi')

print(db.get_messages(addr, 'password'))

print(db.remove_message(addr, msg, 'password'))


addr = db.add_store('pw')

print(db.get_store(addr, 'pw'))

print(db.set_store(addr, 'pw', '<stored data>'))
print(db.get_store(addr, 'pw'))
