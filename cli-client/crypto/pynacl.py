"""
PyNaCl (libsodium) implementation of the Colibri cryptography interface

Colibri needs to process:
    -addresses (optionally signed, sealed messages)
    -rooms

Each cryptography algorithm/library has its own requirements. Libsodium, for example, is better suited to using 2 different algorithms (Curve25519 and Ed25519) for asymetric encryption and signatures. Although the decision to use these two algorithms is very reasonable, this means that Colibri has to adapt to more than straight GPG/RSA or RSA-like algorithms.

In order to be crypto library agnostic, Colibri uses a high level module level interface. Each crypto module must implement RoomKeys, BroadcastKeys and AddressKeys, and manage cryptography, serialization, and key types versioning (to stay compatibility with future changes in cryptography choices).
"""


#import nacl
from nacl.public import PrivateKey, Box, SealedBox
from nacl.secret import SecretBox
from nacl.utils import random
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError

import json

from errors import BadSignature, BadSigningKey


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

def encrypted(key, thing):
    return key.encrypt(thing.encode(), encoder=HexEncoder).decode()
def decrypted(key, thing):
    return key.decrypt(thing.encode(), encoder=HexEncoder).decode()


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
            self.verify_key = self.sign_key.verify_key
            self.access_key = SecretBox(random(SecretBox.KEY_SIZE))

    def publish(self, data):
        # sign + encrypt
        # optional: embed signing key ?

        # split the message from its signature
        # https://pynacl.readthedocs.io/en/latest/signing/
        signed = self.sign_key.sign(data.encode(), encoder=HexEncoder)
        signature = signed.signature.decode()

        verify_key = self.verify_key.encode(encoder=HexEncoder).decode()
        published = json.dumps({
            "message": data,
            "signature": versioned(signature),
            "verify-key": versioned(verify_key),
        })
        return json.dumps(versioned(encrypted(self.access_key, published)))

    # return False if error (wrong signing key or invalid signature)
    def view(self, data): # -> bool, str
        encrypted_package = json.loads(data)
        assert encrypted_package["format"] == "libsodium-hex"
        assert encrypted_package["version"] == "0.1.0"

        enc = encrypted_package["data"]
        dec = decrypted(self.access_key, enc)
        published = json.loads(dec)

        verify_key = published["verify-key"]
        message = published["message"]
        signature = published["signature"]

        # the signing key must be the same, or the message is corrupt
        assert verify_key["format"] == "libsodium-hex"
        assert verify_key["version"] == "0.1.0"
        if verify_key["data"] != encoded(self.verify_key):
            raise BadSigningKey

        assert signature["format"] == "libsodium-hex"
        assert signature["version"] == "0.1.0"
        encoded_signature = signature["data"].encode()
        # remove the hex encoding
        decoded_signature = HexEncoder.decode(encoded_signature)
        try:
            self.verify_key.verify(message.encode(), decoded_signature)
            return message
        except BadSignatureError as e:
            # return generic Colibri error
            raise BadSignature


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

# mails: signature optional (perfect with Curve25519 ?), asymetric encryption
# each set of keys must be serializable, and shareable (export,...) with a type/version

class AddressKeys:
    key_version = 0.1
    key_type = "libsodium"

    def __init__(self, random_init=True):
        if random_init:
            self.sign_key = SigningKey.generate()
            self.encrypt_key = PrivateKey.generate()

