# Colibri

A protocol for encrypted and untraceable communications.

# Status

Not useable yet, but soon™.

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

See [PROTOCOL.md](./PROTOCOL.md) for the protocol details.

# How to use

The server is a python HTTP server with a local sqlite database. It can be run in any configuration (as long as the address of the server can be accessed from the outside). The server receives messages for addresses, and saves the encrypted chats.

The client is a CLI script. It can be used to generate and output addresses (to receive messages), create chat rooms, send invites, and edit the room chat history.

In order to have an actual conversation, an other tool must be used to edit a chat and send the updates to the servers.


