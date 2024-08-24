"""
PyNaCl (libsodium) implementation of the Colibri cryptography interface

Colibri needs to process:
    -addresses (optionally signed, sealed messages)
    -rooms

Each cryptography algorithm/library has its own requirements. Libsodium, for example, is better suited to using 2 different algorithms (Curve25519 and Ed25519) for asymetric encryption and signatures. Although the decision to use these two algorithms is very reasonable, this means that Colibri has to adapt to more than straight GPG/RSA or RSA-like algorithms.

In order to be crypto library agnostic, Colibri uses a high level module level interface. Each crypto module must implement RoomKeys, BroadcastKeys and AddressKeys, and manage cryptography, serialization, and key types versioning (to stay compatibility with future changes in cryptography choices).
"""


#import nacl
from nacl.public import PrivateKey, PublicKey, Box, SealedBox
from nacl.secret import SecretBox
from nacl.utils import random
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError

import json

from errors import BadSignature


# todo: find when to use the Box in the protocol ?
# Box(private1, public2).encrypt()/.decrypt()
# Box can send signed and encrypted messages at the same, with a single Curve25519 algorithm


# libsodium is supposed to be compatible accross its implementations and bindings in any language
# everything is serialized as hex strings with HexEncoder
library = "libsodium-hex"

# All the crypto library modules must match the same interface to be useable by the Colibri codebase
# bumping the interface version here and in both Colibri will prevent other modules from running until they are up to date
#
# the interface version is irrelevant to the protocol and the cryptography
interface_version = "0.1.0"

# when this module is updated, the serialization format may change and additional code has to be written to stay compatible with the old format
module_version = "0.1.0"


# helper functions

def versioned(encoded_data):
    return {
        "format": library,
        "version": module_version,
        "data": encoded_data,
    }

def encoded(thing):
    return thing.encode(encoder=HexEncoder).decode()
# call <constructor>(encoded.encode(), encoder=HexEncoder)
#def decoded(thing):
#    raise NotImplementedError

def encrypted(key, data):
    return key.encrypt(data.encode(), encoder=HexEncoder).decode()
def decrypted(key, data):
    return key.decrypt(data.encode(), encoder=HexEncoder).decode()

def signed(key, data):
    return key.sign(data.encode(), encoder=HexEncoder).decode()
def verified(key, signed_message):
    try:
        return key.verify(signed_message.encode(), encoder=HexEncoder).decode()
    except BadSignatureError:
        raise BadSignature

def sealed(public_key, data):
    return SealedBox(public_key).encrypt(data.encode(), encoder=HexEncoder).decode()
def unsealed(private_key, data):
    return SealedBox(private_key).decrypt(data.encode(), encoder=HexEncoder).decode()


# rooms use a single symetric key
# (rooms rely on empirical deniability through lack of authentication)
class RoomKeys:
    def __init__(self, random_init=True):
        if random_init:
            self.key = SecretBox(random(SecretBox.KEY_SIZE))


    def encrypt(self, data):
        return versioned(encrypted(self.key, data))

    def decrypt(self, data):
        assert data["format"] == "libsodium-hex"
        assert data["version"] == "0.1.0"
        return decrypted(self.key, data["data"])

    def to_json(self):
        # format versioning is for the entire RoomKeys object
        return json.dumps(versioned({
            "key": encoded(self.key),
        }))

    @staticmethod
    def from_json(data):
        data = json.loads(data)
        assert data["format"] == "libsodium-hex"
        assert data["version"] == "0.1.0"
        data = data["data"]
        encoded_key = data["key"].encode()

        self = RoomKeys(random_init=False)
        self.key = SecretBox(encoded_key, encoder=HexEncoder)
        return self


# broadcasts use a signing key to authenticate the author, and a symetric key to share read access
class BroadcastKeys:
    def __init__(self, random_init=True):
        if random_init:
            self.sign_key = SigningKey.generate()
            print("sign key length:", len(bytes(self.sign_key)))
            self.verify_key = self.sign_key.verify_key
            print("verify key length:", len(bytes(self.verify_key)))
            self.access_key = SecretBox(random(SecretBox.KEY_SIZE))

    def publish(self, data):
        # sign + encrypt
        # optional: embed signing key ?

        signed_message = signed(self.sign_key, data)

        enc = encrypted(self.access_key, signed_message)
        return json.dumps(versioned(enc))

    def view(self, data):
        encrypted_package = json.loads(data)

        assert encrypted_package["format"] == "libsodium-hex"
        assert encrypted_package["version"] == "0.1.0"

        signed_message = decrypted(self.access_key, encrypted_package["data"])

        # will raise an exception if the signature is not correct
        message = verified(self.verify_key, signed_message)
        return message


    def to_json(self):
        returned = {
            "access-key": encoded(self.access_key),
        }
        if self.sign_key is not None:
            returned["sign-key"] = encoded(self.sign_key)
        else:
            returned["verify-key"] = encoded(self.verify_key)
        return json.dumps(versioned(returned))

    @staticmethod
    def from_json(data):
        data = json.loads(data)
        assert data["format"] == "libsodium-hex"
        assert data["version"] == "0.1.0"
        data = data["data"]

        self = BroadcastKeys(random_init=False)

        encoded_access_key = data["access-key"]
        self.access_key = SecretBox(encoded_access_key, encoder=HexEncoder)
        if "sign-key" in data:
            encoded_sign_key = data["sign-key"]
            self.sign_key = SigningKey(encoded_sign_key, encoder=HexEncoder)
            self.verify_key = self.sign_key.verify_key
        else:
            encoded_verify_key = data["verify-key"]
            self.sign_key = None
            self.verify_key = VerifyKey(encoded_verify_key, encoder=HexEncoder)

        return self

# mails: asymetric encryption, with optional signatures (must be known beforehand)
# each set of keys must be serializable, and shareable (export,...) with a type/version

class AddressKeys:
    def __init__(self, random_init=True):
        if random_init:
            self.sign_key = SigningKey.generate()
            self.verify_key = self.sign_key.verify_key
            self.decrypt_key = PrivateKey.generate()
            self.encrypt_key = self.decrypt_key.public_key


    # seal/send_to
    def send(self, data):
        return json.dumps(versioned(sealed(self.encrypt_key, data)))

    # unseal/receive
    def receive(self, data):
        encrypted_package = json.loads(data)
        assert encrypted_package["format"] == "libsodium-hex"
        assert encrypted_package["version"] == "0.1.0"

        message = unsealed(self.decrypt_key, encrypted_package["data"])
        return message

    #def sign(self, data):
    #    #return versioned(signed(
    #    pass

    #def verify(self):
    #    pass

    def to_json(self):
        data = {}
        if self.sign_key is not None:
            data["sign-key"] = encoded(self.sign_key)
        else:
            data["verify-key"] = encoded(self.verify_key)

        if self.decrypt_key is not None:
            data["decrypt-key"] = encoded(self.decrypt_key)
        else:
            data["encrypt-key"] = encoded(self.encrypt_key)

        return json.dumps(versioned(data))

    @staticmethod
    def from_json(data):
        data = json.loads(data)
        assert data["format"] == "libsodium-hex"
        assert data["version"] == "0.1.0"
        data = data["data"]

        self = AddressKeys(random_init=False)
        if "sign-key" in data:
            self.sign_key = SigningKey(data["sign-key"], encoder=HexEncoder)
            self.verify_key = self.sign_key.verify_key
        else:
            self.verify_key = VerifyKey(data["verify-key"], encoder=HexEncoder)

        if "decrypt-key" in data:
            self.decrypt_key = PrivateKey(data["decrypt-key"], encoder=HexEncoder)
            self.encrypt_key = self.decrypt_key.public_key
        else:
            self.encrypt_key = PublicKey(data["encrypt-key"], encoder=HexEncoder)

        return self

