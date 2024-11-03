from crypto.pynacl import RoomKeys, BroadcastKeys, AddressKeys
import json


def test_roomkeys():
    roomkeys = RoomKeys()
    #print(roomkeys.key)
    #print(roomkeys.to_json())

    # serialize
    serialized = roomkeys.to_json()
    parsed = RoomKeys.from_json(serialized)
    assert bytes(roomkeys.key) == bytes(parsed.key)

    # encrypt
    encrypted = roomkeys.encrypt("test")
    decrypted = roomkeys.decrypt(encrypted)
    assert decrypted == "test"
    # encrypted messages must be json-serializable
    assert json.loads(json.dumps(encrypted)) == encrypted


def test_broadcastkeys():
    keys = BroadcastKeys()

    # sign+encrypt
    encoded = keys.publish("test")
    assert keys.view(encoded) == "test"

    # serialize
    serialized = keys.to_json()
    parsed = BroadcastKeys.from_json(serialized)
    assert bytes(parsed.access_key) == bytes(keys.access_key)
    assert type(serialized) == str

    # export public keys
    view_keys = keys.public()
    assert view_keys.sign_key == None
    assert bytes(view_keys.verify_key) == bytes(keys.verify_key)
    assert bytes(view_keys.access_key) == bytes(keys.access_key)


def test_addresskeys():
    sender = AddressKeys()
    receiver = AddressKeys()

    # encryption
    sealed = receiver.send("test")
    assert receiver.receive(sealed) == "test"

    # serialization
    serialized = receiver.to_json()
    parsed = AddressKeys.from_json(serialized)
    assert bytes(parsed.sign_key) == bytes(receiver.sign_key)
    assert bytes(parsed.verify_key) == bytes(receiver.verify_key)
    assert bytes(parsed.encrypt_key) == bytes(receiver.encrypt_key)
    assert bytes(parsed.decrypt_key) == bytes(receiver.decrypt_key)

    # export public keys
    sender_public = sender.public()
    assert sender_public.sign_key == None
    assert sender_public.decrypt_key == None
    assert bytes(sender_public.verify_key) == bytes(sender.verify_key)
    assert bytes(sender_public.encrypt_key) == bytes(sender.encrypt_key)

