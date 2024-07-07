import system

key = system.create_key()
print(key)
encrypted = system.encrypt(key, 'test-message')
print(encrypted)
decrypted = system.decrypt(key, encrypted)
print(decrypted)

print(system.create_room())
