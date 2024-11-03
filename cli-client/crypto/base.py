"""
abstract interface for Colibri crypto implementations
"""

class RoomKeys:
    def __init__(self):
        raise NotImplementedError

    def encrypt(self, data):
        raise NotImplementedError

    def decrypt(self, data):
        raise NotImplementedError

    # export public keys, by returning a RoomKeys object without the private keys
    # this method has no meaning for rooms (symetric encryption only)
    def public(self):
        # DO NOT implement this method (as it makes no sense)
        raise NotImplementedError("This should not happen")

    # return True if the private keys are stored in this instance
    @property
    def owned(self):
        return True

    def to_json(self):
        raise NotImplementedError

    @staticmethod
    def from_json():
        raise NotImplementedError

class AddressKeys:
    def __init__(self):
        raise NotImplementedError

    # encrypt/decrypt
    def seal(self, data, sign=False):
        raise NotImplementedError

    def unseal(self, data):
        raise NotImplementedError

    # signatures are optional
    def sign(self, data):
        pass

    def verify(self, data):
        pass

    def public(self):
        raise NotImplementedError

    # return True if the private keys are stored in this instance
    @property
    def owned(self):
        raise NotImplementedError

    def to_json(self):
        raise NotImplementedError

    @staticmethod
    def from_json():
        raise NotImplementedError


class BroadcastKeys:
    def __init__(self):
        raise NotImplementedError

    # sign+encrypt
    def publish(self, data):
        raise NotImplementedError

    # decrypt+verify
    def view(self, data):
        raise NotImplementedError

    def public(self):
        raise NotImplementedError

    # return True if the private keys are stored in this instance
    @property
    def owned(self):
        raise NotImplementedError

    def to_json(self):
        raise NotImplementedError

    @staticmethod
    def from_json():
        raise NotImplementedError

