# Protocol

## For the user

There are 3 ways to communicate with Colibri:
- Rooms
- Addresses
- Broadcasts

### Rooms

Chatrooms are simply stored as an encrypted blob on a server. They are encrypted with a symetric key, shared by all the users.

Uses:
- Private messages between two peers
- Servers for small communities

Unlike other messaging services, Colibri does not authenticate room users. Any user can impersonate other members, alter messages or even remove the entire chat history. This means Colibri alone does not make it possible to prove that your messages were written by you.

Example:
```sh
.venv/bin/python client.py new-room
```


### Addresses

Addresses, like e-mail addresses, are a way for other people to send you messages. Each address has its own private key to decrypt received messages. The server will stores the encrypted messages until told otherwise by the owner of the address.

Uses:
- Receiving private messages
- Receiving invites to rooms
- Receiving contact information for broadcasts and other addresses

Example:
```sh
.venv/bin/python client.py new-address
```


### Broadcasts

Broadcasts are a way for Colibri users to share content one-sidedly, using authentication to prevent impersonation. Broadcasts work the same way as a personal blog: the owner can publish and edit their content, and the users can read the content knowing there is a single author.

Uses:
- Sharing resources

Example:
```sh
.venv/bin/python client.py new-broadcast
```

### Servers

Rooms, Addresses and Broadcasts are all stored on remote servers. Knowing at least one server is required before registering a new room/address/broadcast.

Example:
```sh
.venv/bin/python client.py add-server "https://localhost:8000"
.venv/bin/python client.py trust-server "https://localhost:8000"
```

Follow the setup instructions at [the server readme](./server/README.md) to setup a local Colibri server




## For the auditor

The protocol manages:
- Servers
- Rooms
- Addresses
- Broadcasts
- Messages
- Invites

### Servers

Servers are very simple, and do not manage any encryption. They just expose an HTTP API (this implementation uses FastAPI), and store everything locally.

There is a simple authentication system to prevent a third party from reading an address or broadcasting, but this is just for spam prevention. Since the individual value of an auth token is weak (everything is encrypted or signed outside of the server), there is no currently no security over server authentication.

A correct server (one that is not rogue) will minimize the amount of retained information about what is saved. The default Colibri server implementation will use random UUIDs (v4) as ids for rooms, addresses, messages and broadcasts, to prevent ordering the elements in the database, does not log dates, and does not feature a way to list the registered entries in its storage.

For more info about the server's API, setup a local instance (FastAPI provides an automatically generated documentation).

Note: the API uses a non-standard practice (sending a JSON body in a GET request). This is done in order to simplify the API, and should not create any problem since both FastAPI and Requests support it. This has already been done before by ElasticSearch before.


### Rooms

Rooms are stored as a simple encrypted variable. To the server, each room is a blob with no metadata like the number of messages.
The Room users synchronize by only writing on the server if the hash of the current state of the room is known.

The value stored in this black box is a JSON message that looks like this:
```json
{
    "members": [
        "a": {
            "public-key": "BEGIN PGP PUBLIC KEY …\n"
        }
    ],

    "messages": [
        {
            "author": "a",
            "type": "text",
            "text": "# Hello"
        }
    ]
}
```

Note that this example does not follow the exact structure used in Colibri.

At the time of writing, this JSON formatting is not implemented in this repository because the user-level features are not part of the encryption protocol. From the Colibri CLI client, a Room is just a store for a single encrypted text.

To give someone access to a Room, it is recommanded to send an Invite to their Address (since the Room access information will be encrypted) to prevent leaking the Room encryption key.


### Addresses

Addresses are encoded as Message lists on the Colibri server.
Each Message is a JSON message encrypted with the public key on the address.

Messages can contain human readable text, or other types of messages specific to Colibri, like a Room access details (Invite).

Messages are only deleted by the server when told to do so by the client.


### Broadcasts

Like Rooms, broadcasts are encoded as an encrypted store to control access. However, in addition to the symetric key, an asymetric key is used by the owner to sign their content.


The value stored in the encrypted storage is a JSON message of this type:
```json
{
    "data": "hi",
    "signature": "BEGIN PGP …\n"
}
```

To prevent other people from overwriting on someone else's broadcast, the server uses authentication to restrict write access. However, it is the role of the client to verify signatures.

