"""
Subprocess and file interaction
"""

from subprocess import PIPE, Popen
from uuid import uuid4 as uuid
import os

import db


def syscall(cmd, stdin=None):
    "statuscode, stdout, stderr = system(command[, stdin])"
    if stdin is not None:
        stdin = stdin.encode()
    p = Popen(
            cmd,
            shell=True,
            stdout=PIPE,
            stderr=PIPE)
    out, err = p.communicate(stdin)
    out = out.decode()
    err = err.decode()
    return p.returncode, out, err


def create_key():
    # return name
    while True:
        name = str(uuid())
        if not os.path.exists(f"data/keys/{name}.public.asc"):
            break
    syscall(f"./sgpg/create-key data/keys/{name}")
    return name

# TODO
def encrypt(key_name, message):
    pass

def decrypt(key_name, message):
    pass

# these features are not used currently
#def sign(key_name, message):
#    pass

#def verify(key_name, message):
#    pass


def sym_encrypt(aes_key, message):
    pass

def sym_decrypt(aes_key, message):
    pass


"""
"""

def create_store():
    while True:
        name = str(uuid())
        if not os.path.exists(f"data/rooms/{name}"):
            os.mkdir(f"data/rooms/{name}")
            return name
