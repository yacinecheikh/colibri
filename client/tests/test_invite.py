from subprocess import PIPE, Popen, STDOUT
import os

verbose = False
def debug(msg):
    if verbose:
        print(f"[DEBUG] {msg}")

def info(msg):
    print(f"[INFO] {msg}")


def syscall(cmd, stdin=None):
    "statuscode, stdout, stderr = system(command[, stdin])"
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


def run(profile, cmd, stdin=None):
    info(f"running: {profile}/client.py {cmd}")
    code, out = syscall(f"cd {profile} && .venv/bin/python client.py {cmd}", stdin)
    debug("done")
    debug(f"return code: {code}")
    info(f"output:\n{out}")
    # the return code is not used by the colibri client
    return out

def create_profile(name):
    debug(f"creating profile {name}")
    if os.path.exists(name):
        debug("removing existing files")
        syscall(f"rm -rf {name}")
    os.mkdir(name)
    os.mkdir(f"{name}/data")
    os.mkdir(f"{name}/data/keys")
    os.mkdir(f"{name}/data/rooms")
    files = [
        "net.py",
        "system.py",
        "client.py",
        "datatypes.py",
        "communication.py",
        "db.py",

        "init.sql",
        "requirements.txt",
    ]
    for f in files:
        syscall(f"cp ../{f} {name}/")
    debug("imported source code")
    syscall(f"git clone https://github.com/yacinecheikh/sgpg {name}/sgpg")
    debug("cloned sgpg")
    syscall(f"cd {name} && python3 -m venv .venv")
    debug("created venv")
    syscall(f"cd {name} && .venv/bin/pip install -r requirements.txt")
    debug("installed dependencies")
    run(name, "add-server http://localhost:8000")
    #syscall(f"cd {name} && .venv/bin/python client.py add-server http://localhost:8000")
    info(f"created profile {name}")



create_profile("sender")
create_profile("receiver")

room = run("sender", "new-room")[:-1]
addr = run("receiver", "new-address")[:-1]
exported = run("receiver", f"export-address {addr}")
run("sender", "import-address", exported)
run("sender", f"send-invite {addr} {room}")
run("receiver", f"read-address {addr}")
run("sender", "describe")
run("receiver", "describe")
