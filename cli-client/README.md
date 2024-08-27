# Colibri cli client

## Setup

Create a python virtual environment:
```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Running tests

Colibri tests are split into unit tests and integration tests.

Unit tests are simple pytest modules, doing what is expected of unit tests. They are used to detect regressions and simplify debugging.

Integration tests can be found in the `tests` folder. They also run as pytest units, but each test function creates cli client folders dynamically. They are uused to automate testing interactions between multiple clients (contact exchange,...).


Important note:
Some tests require a server to communicate with. In order to run those, you must run a local server at localhost:8000. The instructions on how to do that are in the [server readme](../server/README.md). If you skip that part, these tests will all fail.


To run all tests:
```sh
.venv/bin/pytest
```

To only run tests that do not require a local server instance:
```sh
.venv/bin/pytest -m "not net"
```



## How to use

To run the CLI:
```sh
.venv/bin/python client.py
```

The `client.py` script contains all the required commands to communicate with servers and other clients (generating message addresses, editing a chat room,…).

By itself, the CLI client is not supposed to be used manually (the CLI is too low level). Instead, you should use a frontend to edit chat rooms in markdown for example.

The local cache is saved in the `data/` folder. Ideally, you should encrypt the entire software (in a LUKS-encrypted usb key for example) to prevent scanning or modification attempts by malicious programs.


## Remote/local storage

Messages that are stored on the server are not automatically remove when downloaded (since a failure could lose the messages).
Instead, messages have tags to identify them, and can be selected for removal locally (with the `remove-message` command) or remotely (`remove-remote-messages`)

If a message is removed locally but kept on the server, it will be downloaded again during the next update. To delete a message definitely, remove the server (remote) message before the local one.

In order to obfuscate which messages are read on the server, the client downloads every message at each update. This can cause lag on slow connections. To solve this problem, just remove the remote messages with `remove-remote-messages`. Once a message is removed from the remote server, it will never be downloaded again.

If an invite message is regenerated (by removing the local message before updating), the invite will also be regenerated if it had been removed. To avoid regenerating removed messages, remove them from the server.


