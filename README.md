# Colibri

A protocol for encrypted and untraceable communications.

## Status

Colibri consists of 3 parts:
- The server: the server simply stores encrypted blobs and creates locally unique ids to address these packages. The server has the main features done and tested.
- The CLI client: this script contains all the commands to interact with the server and with other users securely. However, the CLI client is not intended for the end user. Its purpose is to be used as a backend by other programs, such as a GUI or a mobile app. The CLI client should be over soon (in a matter of days)
- The GUI frontend: this part is not in the repository yet. This is the part that the end user is most interested in, but the CLI client must have a functional API before the GUI can use it.
- The protocol: the protocol needs to be documented in order to verify that the program is correct and secure. The documentation must be centralized and kept up to date.


## Motivations (why yet another secure messaging system)

There are already many secure messaging systems, like Signal or Matrix, which make a very good job of securing the message content itself.

Colibri was made with these goals in mind:
- Being simple enough for anyone to audit and host at home over Tor or I2P
- Third parties should not be able to know who wrote to whom
- Colibri should be useable anonymously from Tor or I2P
- Security should lead the design over convenience. In particular, plausible deniability in private exchanges can be made into a funny feature by simply giving the users the freedom to impersonate themselves.
- Bots should not be discriminated against
- Requiring a phone number to register is blasphemy


## Protocol

See [PROTOCOL.md](./PROTOCOL.md) for the protocol details.

## How to use

The server (node) is where users register new addresses and store their chat history. It can be run in any configuration, as long as the server can be connected to by the end user.
To setup your own server: see [the server readme](./server/)

The CLI client is a low level python script to interact with the server and with other users.
To install the CLI client: see [the client readme](./client/).

## Future plans

These ideas will not be considered until the base service works.

- In order to improve the reactivity, the server and CLI client will probably need some kind of event streaming feature to allow the server to send events to the client.
- Some additional features, like bridges, will have to be implemented as external bots in order to keep the code base small. To do this, a special type of message could be created to allow custom extensions to exchange data.

