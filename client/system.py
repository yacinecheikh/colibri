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
gpg calls
"""

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
    return syscall(f"./sgpg/encrypt data/keys/{key_name}.public.asc", message)[1]

def decrypt(key_name, message):
    return syscall(f"./sgpg/decrypt data/keys/{key_name}.private.asc", message)[1]

# TODO: these commands are not secure
# any process running "ps aux" can get the passwords of currently running gpg processes
# additionally, script injections allow the server to generate malicious keys to inject code in bash
def sym_encrypt(sym_key, message):
    return syscall(f"gpg --batch --passphrase {sym_key} -c", message)

def sym_decrypt(sym_key, message):
    return syscall(f"gpg --batch --passphrase {sym_key} -d", message)


"""
fs
"""

def create_room():
    while True:
        name = str(uuid())
        if not os.path.exists(f"data/rooms/{name}"):
            syscall(f'touch data/rooms/{name}')
            return name

def save_key(public_key):
    while True:
        name = str(uuid())
        if not os.path.exists(f"data/keys/{name}.public.asc"):
            with open(f'data/keys/{name}.public.asc', 'w') as f:
                f.write(public_key)
            return name

