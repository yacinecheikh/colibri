# Colibri

A protocol for encrypted and untraceable communications.

# Motivations (complaints with existing services)

- Though most communication systems do a good job at hiding the content of a communication, most of them do not hide the existence of the communication itself.
- Signal requires a phone number, which makes me feel dirty. A truly private communication system has to be compatible with tor, i2p, someone else's computer,... and should try to make identities as volatile as possible.
- Plausible deniability is a joke (the average \<X\> user can't even modify messages from other people)

The compromise I found in order to compete with secure communication giants is:
- Do not attempt to reinvent cryptography
    - Instead, rely on proven tools like GPG
- Do not commit the sin of bloat
    - Instead, keep the code auditable by any developper who understands asymetric cryptography
- Do not ask for trust
    - Instead, let the open source clients manage encryption and let the users host their own servers
- Do not ask for a name
    - Instead, let the clients create random identities for every communication
- Enable features that are made natural by the cryptographic algorithms, instead of following hard-coded specifications.

# Protocol

The protocol features:
- Messages: messages sent to a public key in order to initiate a comminication
- Communications: initiated communications between 2 (or more ?) users. In a communication, all the users share a common symetric key to edit the communication history. In pratice, this means any user can impersonate anyone in a chat room. This is a feature. Trust me, nothing could go wrong.
- Nodes: storage servers to keep encrypted messages and communications, ideally without leaking everything.

### Interactions with other users

Users can:
- Establish a communication
- Move an existing communication somewhere else
- Modify the state of the communication

### Interactions with a storage server

Users can:
- Create a random address to receive messages
- Create a random address to store a conversation
- Secure their addresses against spam with (auto-generated) authentication tokens

### Storage servers

Ideally, a node would not leak the encrypted packages and would hide the existence of addresses from the unauthenticated.
However, since a third party server cannot be trusted to keep its users' privacy, this may not be the case. In the worst case, a large organization with a high processing power could be trying to download every encrypted communication in the hope of decrypting it later.
For this reason, users should try to host their own nodes as much as possible.


Note on the API:
Every request, including GET requests, use a JSON body as a query.
Sending a body in GET may seem weird, but it is allowed and makes sense as long as the GET query is used to fetch data from the server and is not cached/bookmarked in a browser.
Doing so allows me to streamline the API and only use JSON instead of encoding authentication tokens in the url.


Message API:
```
POST /message/register
{
    "auth": "<my auth token>"
}
Returns:
"<address>"

GET /message/{address}
{
    "auth": "<my auth token>"
}
Returns:
[
    {
        "id": "<message id>",
        "data": "<encrypted data>"
    },
    …
]

POST /message/{address}
{
    "data": "<encrypted data>"
}
Returns:
"ok"

DELETE /message/{address}
{
    "auth": "<my auth token>",
    "remove": [
        "<message id>",
        …
    ]
}
Returns:
[
    "ok",
    …
]
```

Communication storing API:
```
POST /store/register
{
    "auth": "<my store auth token>"
}
Returns:
"<address>"

GET /store/{address}
{
    "auth": "<my store auth token>"
}
Returns:
"<data>"

POST /store/{address}
{
    "auth": "<my store auth token>",
    "data": "<data>"
}
Returns:
"ok"
```

# Implementation

