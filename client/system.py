from subprocess import PIPE, Popen

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
    pass

# TODO
def encrypt(key_name):
    pass
