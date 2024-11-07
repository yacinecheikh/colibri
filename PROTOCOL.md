# Protocol

## Useage

### Definitions

Colibri features 3 ways to communicate:
- Rooms
- Addresses
- Broadcasts

An average user would typically use multiple rooms, multiple addresses and multiple broadcasts at the same time.
Each communication channel is independant from the others, and can be located on any server.

These communication channels can be used for private messages, signatures or sharing content. However
The encrypted communications are stored on servers. Each communication channel (room, address or broadcast) has a unique id on any server and can be on any server.

#### Servers

Colibri server instances are simple HTTP servers with a JSON API and an embedded database.

They feature a basic token-based authentication to store and retrieve data.
Colibri servers do not require users to authenticate in order to create and use communication channels.

In order to distribute communications and to avoid relying on a compromised server, it is recommended for clients and hosters to prefer using many small servers over a large one.

[//]: # (TODO: add a diagram with the room/address/broadcast distribution)


#### Rooms

A rooms is a simple symetrically encrypted storage on a server.

This type of communication can be used to communicate without associating your identity with your messages.

To prevent spam and encrypted data collection, the server requires a token for read/write access to the room.

Since the only cryptography used is symetrical, there is no builtin mechanism to attribute messages to a user. This is useful for plausible deniability.


#### Addresses

Addresses are an encrypted storage for messages on a server.
Addresses use asymetric encryption to allow anyone to send encrypted messages, but only the address owner to decrypt them.

This type of communication can be used to create a public contact point and exchange room access keys.

The auth token authenticates the address owner to prevent third parties from collecting the encrypted messages.

#### Broadcasts

Broadcasts are a signed and encrypted storage on a server.
The broadcast owner can edit the contents of a broadcast and sign it, and the broadcast viewers can decrypt it.

This type of communication can be used to host static resources like a website.

The auth token authenticates the broadcast owner to prevent viewers from destroying the broadcasted content.


### CLI client API


There are 3 ways to communicate with Colibri:
- Rooms
- Addresses
- Broadcasts

#### Rooms

Chat rooms are the main way of communication with known users. Their contents are encrypted from the outside.
Rooms do not have any member authentication feature. As long as a user has access to a room, they can edit or remove messages from others anonymously.

The server is unaware of what data is stored in a room, and can only store the new state of a room when someone updates the room.

##### Main uses

The main reason to use a room is to avoid having legal responsability of what is being said, since messages cannot be attributed.

Examples:
- Private messages between two peers, where identity is not a problem
- servers for small communities, where trust is enough to protect the room


##### Implementation details
To prevent race conditions, the users must validate the previous known state of the room when writing to it.
To prevent spam or data collection from entities with no cryptographic access, a random password is required to read and write from the room state. This password is shared along with the encryption keys of the room.

[//]: # "Security against attacks:"
[//]: # "While a rogue server or a third party could collect the IP addresses of the users and collect the encrypted data, an anonymous internet connection is enough to prevent the former, and random data junk will sabotage the storage capacity of the later, since each new update is as big as the entire chat history."

Unlike other messaging services, Colibri does not authenticate room users. Any user can impersonate other members, alter messages or even remove the entire chat history. This means Colibri alone does not make it possible to prove that your messages were written by you.


##### CLI client example:
```sh
# create a new room on the local server
$ .venv/bin/python client.py new-room http://localhost:8000
6b6e42a7-b89e-4917-a332-9272bdba5341
$ .venv/bin/python client.py list-rooms
6b6e42a7-b89e-4917-a332-9272bdba5341

# send a message (upload it on the server)
$ .venv/bin/python client.py write-room 6b6e42a7-b89e-4917-a332-9272bdba5341@http://localhost:8000 "hi there"
# read it (download it from the server)
$ .venv/bin/python client.py read-room 6b6e42a7-b89e-4917
hi there

# export the room keys
$ .venv/bin/python client.py export-room 6b6e42a7-b89e-4917-a332-9272bdba5341@http://localhost:8000 > my-room.json
# import on an other machine
$ cat my-room.json | .venv/bin/python client.py import-room

# override remote data and forget about the room
# the server will still keep an empty room, with nothing inside
$ .venv/bin/python client.py write-room 6b6e42a7-b89e-4917-a332-9272bdba5341@http://localhost:8000 ""
$ .venv/bin/python client.py remove-room 6b6e42a7-b89e-4917-a332-9272bdba5341@http://localhost:8000
```


#### Addresses

Addresses, like e-mail addresses, are a way for other people to send you messages. Each address has its own private key to decrypt received messages. The server will stores the encrypted messages until told otherwise by the owner of the address.

Uses:
- Sending and receiving signed and encrypted messages
- Receiving contact information to rooms, broadcasts and other addresses

Note: Signing messages is not implemented yet.

##### CLI client example
```sh
# create a new address
$ .venv/bin/python client.py new-address http://localhost:8000
60fd8f6a-c1de-4fce-9f0a-de921b11e1c6
$ .venv/bin/python client.py list-addresses
60fd8f6a-c1de-4fce-9f0a-de921b11e1c6@http://localhost:8000

# exchange contact information
$ .venv/bin/python client.py export-address-info 60fd8f6a-c1de-4fce-9f0a-de921b11e1c6@http://localhost:8000 > my-address.json
$ cat friend-address.json | .venv/bin/python client.py import-address
$ .venv/bin/python client.py list-foreign-addresses
af71622b-c64e-4044-8119-3a9b315cda2a@theartofmonero.com/colibri

# send a message
$ .venv/bin/python client.py send-message af71622b-c64e-4044-8119-3a9b315cda2a@theartofmonero.com/colibri "hi there"

# receive a message
$ .venv/bin/python client.py fetch-messages af71622b-c64e-4044-8119-3a9b315cda2a@theartofmonero.com/colibri
8f750e98-5504-4e0f-9915-9b6bb7600ff6@af71622b-c64e-4044-8119-3a9b315cda2a@theartofmonero.com/colibri
$ .venv/bin/python client.py read-message 8f750e98-5504-4e0f-9915-9b6bb7600ff6@af71622b-c64e-4044-8119-3a9b315cda2a@theartofmonero.com/colibri
hi there
```

[//]: # (TODO: add more example commands for message management)


#### Broadcasts

Broadcasts are a way for Colibri users to share content in a one-sided way, using authentication and signatures to prevent impersonation. Broadcasts work the same way as a personal blog: the owner can publish and edit their content, and the users can read the content knowing there is a single author.

Uses:
- Sharing static resources

##### CLI client example
```sh
$ .venv/bin/python client.py new-broadcast http://localhost:8000
5129cc67-abe4-4c6a-a563-4a8786dd88bb@http://localhost:8000
$ .venv/bin/python client.py list-broadcasts
5129cc67-abe4-4c6a-a563-4a8786dd88bb@http://localhost:8000

# export view access
$ .venv/bin/python client.py export-broadcast-info 5129cc67-abe4-4c6a-a563-4a8786dd88bb@http://localhost:8000 > my-website.json
# import view access
$ cat my-website.json | .venv/bin/python client.py import-broadcast

# publish my website
$ cat website.md | .venv/bin/python client.py write-broadcast 5129cc67-abe4-4c6a-a563-4a8786dd88bb@http://localhost:8000
# people with view access can download it
$ .venv/bin/python client.py read-broadcast 5129cc67-abe4-4c6a-a563-4a8786dd88bb@http://localhost:8000
```

#### Servers

Rooms, Addresses and Broadcasts are all stored on remote servers. These servers have no user authentication and can be used by everyone, as long as they can physically be connected to.

Follow the setup instructions at [the server readme](./server/README.md) to setup a local Colibri server

##### CLI client example
```sh
$ .venv/bin/python client.py add-server "http://localhost:8000"
#$ .venv/bin/python client.py trust-server "http://localhost:8000"  # optional
$ .venv/bin/python client.py list-servers
http://localhost:8000
```





## For the auditor

To verify the Colibri source code, start with the server, as the server codebase is the simplest and can be understood without a client.

### Server

The Colibri server must:
- store encrypted messages
- not store anything else
- prevent third parties from collecting encrypted data

The dependencies of this server implementation are the FastAPI and SQLite Python libraries.
FastAPI has a self-documentation feature, which can be [used by running a Colibri server instance](./server).

### CLI client

The CLI client manages a local server/room/address/broadcast register, with locally saved cryptographic keys.

The dependencies are:
- requests
- libsodium (pynacl)
- sqlite3

Eventually, the CLI client should support more cryptography libraries/algorithms, in order to be resilient against attacks and quantum computers.


### GUI client

The GUI client is not implement yet. However, the GUI client should not do anything security-related by itself, and rely on the CLI client instead.

The main security concern would be that the GUI frontend is not malicious and does not willingly export decryption keys.

