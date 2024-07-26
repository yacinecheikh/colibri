"""
Subprocess and file interaction
"""

from subprocess import PIPE, Popen
from uuid import uuid4 as uuid
import os

import db
#from datatypes import KeyPair


def syscall(cmd, stdin=None):
    "statuscode, stdout, stderr = system(command[, stdin])"
    if stdin is not None:
        stdin = stdin.encode()
    p = Popen(
            cmd,
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE if stdin is not None else None)
    #if stdin is not None:
    #    p.stdin.write(stdin)
    out, err = p.communicate(stdin)
    #out, err = p.communicate()
    out = out.decode()
    err = err.decode()
    return p.returncode, out, err



"""
fs
"""

# keys

def public_key(key_name):
    return f"data/keys/{key_name}.public.asc"

def private_key(key_name):
    return f"data/keys/{key_name}.private.asc"

def new_key():
    while True:
        name = str(uuid())
        if not os.path.exists(public_key(name)):
            return name

def save_key(public, private=None):
    name = new_key()
    with open(public_key(name), "w") as f:
        f.write(public)
    if private is not None:
        with open(private_key(name), "w") as f:
            f.write(private)
    return name


# messages and signatures

def message(name):
    return f"data/signatures/{name}"

def signature(name):
    return f"data/signatures/{name}.asc"

def new_message():
    while True:
        name = str(uuid())
        if not os.path.exists(message(name)):
            return name

def save_message(message_data, signature_data=None):
    name = new_message()
    with open(message(name), "w") as f:
        f.write(message_data)
    if signature_data is not None:
        with open(signature(name), "w") as f:
            f.write(signature_data)
    return name

