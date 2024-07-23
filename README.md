# Colibri

A protocol for encrypted and untraceable communications.

## Status

Colibri consists of 3 parts:
- The server: the server simply stores encrypted blobs and creates locally unique ids to address these packages. The server has the main features done and tested.
- The CLI client: this script contains all the commands to interact with the server and with other users securely. However, the CLI client is not intended for the end user. Its purpose is to be used as a backend by other programs, such as a GUI or a mobile app. The CLI client should be over soon (in a matter of days)
- The GUI frontend: this part is not in the repository yet. This is the part that the end user is most interested in, but the CLI client must have a functional API before the GUI can use it.
- The protocol: the protocol needs to be documented in order to verify that the program is correct and secure. The documentation must be centralized and kept up to date.


## Motivations (why yet another secure messaging system ?)

There are already existing secure messaging systems, like Signal or Matrix, which make a very good job of securing the message content itself.

The main complaints I (still) have with these options are:
- code size: I have yet to find a single messaging system I can audit by myself. This project is supposed to stay small, by reusing the existing and trusted tools like GPG.
- contact obfuscation: generating new accounts for each conversation should not just be normal, it should be encouraged or even automated. Requiring a phone number to register is clearly against the concept of privacy.
- plausible deniability: the idea of using a shared symetric for conversations is underused. I think letting security part of the way the end user uses the app will lead to a funny experience for the user, and make security more natural for the end user.
- Signal requires a phone number to register. At some point I thought about automating GPG and pastebin to send encrypted messages without authenticating and from Tor, and that's probably how Colibri came to be.


## Protocol

See [PROTOCOL.md](./PROTOCOL.md) for the protocol details.

## How to use


The server (node) is where users register new addresses and store their chat history. It can be run in any configuration, as long as the server can be connected to by the end user.
To setup your own server: see [the server readme](./server/)

The CLI client is a low level python script to interact with the server and with other users.
To install the CLI client: see [the client readme](./client/)



## Future plans

These ideas will not be considered until the base service works.

- In order to improve the reactivity, the server and CLI client will probably need some kind of event streaming feature to allow the server to send events to the client.
- Some additional features, like bridges, will have to be implemented as external bots in order to keep the code base small. To do this, a special type of message could be created to allow custom extensions to exchange data.

