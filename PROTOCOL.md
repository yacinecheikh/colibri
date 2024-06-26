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


###### Establishing communications

- User A wants to communicate with user B
- A knows the public key of B and their messaging address
- A generates an address to store a conversation on a server
- A encrypts a message for B, containing a symetric key and the address previously generated
- B reads the message, and can now edit the conversation on the new address

###### Moving communications

- User A wants to move the current conversation to an other place, and renew the keys
- A generates a new asymetric key pair, and sends their public key on the existing conversation
- B reads the invitation to "move out", and can generate an address
- B sends the new conversation details to A
    - Note: this system is not compatible with more than 2 users (since A is the only one who can read the new address)


###### Modifying the state of communications

The users synchronize by downloading and uploading the entire encrypted conversation.
This process is ineffficient, but should not be a problem for text conversations (larger medias could be sent through other, temporary channels for example).

To prevent race conditions, the POST requests must embed a hash of the stored (encrypted) conversation to prevent erasing modifications made by other people.
    - This part is not implemented in the server API yet



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

