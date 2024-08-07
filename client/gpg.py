"""
GPG wrapper
"""

from subprocess import PIPE, Popen
from uuid import uuid4 as uuid
import os

import db
#from datatypes import KeyPair

import system
from system import syscall


def create_key():
    name = system.new_key()
    syscall(f"./sgpg/create-key data/keys/{name}")
    return name

# asymetric encryption (key is the name matching with {key}.public.asc and {key}.private.asc)
def sign(key, message):
    # need to save to files because the sgpg wrapper scripts can only sign files
    name = system.save_message(message)
    syscall(f"./sgpg/sign {system.private_key(key)} {system.message(name)}")
    with open(system.signature(name)) as f:
        return f.read()

def verify(key, message, signature):
    # TODO: document:
    # keys are only imported once, but messages and signatures are imported/removed only as temporary files
    name = system.save_message(message, signature)
    # TODO: use return code to check success
    return_code, out, err = syscall(f"./sgpg/verify {system.public_key(key)} {system.message(name)}")
    # sgpg/verify exits with 0 if the signature is correct
    return return_code == 0

def send(key, message):
    return syscall(f"./sgpg/encrypt {system.public_key(key)}", message)[1]

def receive(key, encrypted):
    return syscall(f"./sgpg/decrypt {system.private_key(key)}", encrypted)[1]

# WARNING
# these commands are not secure against spying from other processes
# any process running the `ps aux`command can get the passwords of running gpg processes
# additionally, these commands are vulnerable against script injections from a rogue peer
# TODO: fix the script injections with shell=False in syscall

# symetric encryption (key is a string)
def encrypt(key, data):
    # TODO: [1]
    return syscall(f"gpg --armor --batch --passphrase {key} -c", data)[1]

def decrypt(key, data):
    return syscall(f"gpg --batch --passphrase {key} -d", data)[1]

