"""
integration testing lib

ensures everything works as intended
"""


from subprocess import PIPE, Popen, STDOUT
import os


verbose = True

def debug(msg):
    if verbose:
        print(f"[DEBUG] {msg}")

def info(msg):
    print(f"[INFO] {msg}")


def syscall(cmd, stdin=None):
    "statuscode, stdout, stderr = syscall(command[, stdin])"
    if stdin is not None:
        stdin = stdin.encode()
    p = Popen(
            cmd,
            shell=True,
            stdout=PIPE,
            stderr=STDOUT,
            stdin=PIPE if stdin is not None else None)
    #if stdin is not None:
    #    p.stdin.write(stdin)
    out, err = p.communicate(stdin)
    #out, err = p.communicate()
    out = out.decode()
    return p.returncode, out


# allows failing
#def run(profile, cmd, stdin=None):
#    info(f"running: {profile}/client.py {cmd}")
#    code, out = syscall(f"cd tests/{profile} && .venv/bin/python client.py {cmd}", stdin)
#    debug("done")
#    debug(f"return code: {code}")
#    info(f"output:\n{out}")
#    # the return code is not used by the colibri client
#    return out


def run(profile, cmd, stdin=None):
    info(f"running: {profile}/client.py {cmd}")
    code, out = syscall(f"cd tests/{profile} && .venv/bin/python client.py {cmd}", stdin)
    if code == 0:
        debug("ok")
    else:
        debug("error")
    if out == "ok\n":
        print()
    else:
        debug(f"output:\n{out}")
    assert code == 0  # indicates an unhandled Python exceptions (the return code is never used by the cli client)
    #debug("ok")
    #debug(f"return code: {code}")
    return out


def create_minimal_profile(name):
    "create a new colibri cli client"
    debug(f"creating profile {name}")
    if os.path.exists(f"tests/{name}"):
        debug("removing existing files")
        syscall(f"rm -rf tests/{name}")
    os.mkdir(f"tests/{name}")

    syscall(f"cp -r *.py init.sql crypto tests/{name}/")
    debug("imported source code")

    syscall(f"ln -s ../../.venv tests/{name}/")
    debug("created venv")


def create_profile(name):
    create_minimal_profile(name)
    run(name, "add-server http://localhost:8000")
    run(name, "trust-server http://localhost:8000")
    info(f"created profile {name}")


#create_profile("sender")
#create_profile("receiver")
#
#room = run("sender", "new-room")[:-1]
#addr = run("receiver", "new-address")[:-1]
#exported = run("receiver", f"export-address {addr}")
#run("sender", "import-address", exported)
#run("sender", f"send-invite {addr} {room}")
#run("receiver", f"read-address {addr}")
#run("sender", "describe")
#run("receiver", "describe")
