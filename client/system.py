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
def encrypt(key_name):
    pass
