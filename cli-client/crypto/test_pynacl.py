from pynacl import RoomKeys, BroadcastKeys, AddressKeys
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

    #print(encrypted)
    #assert False


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

