# Colibri

A protocol for encrypted and untraceable communications.

## Warning

This project is on hiatus due to being too similar to the Simplex chat app.

## Status

- Server: Useable
- CLI client: Useable
- GUI frontend: Not started
- Protocol: Documentation needs to be reviewed by someone else

## Motivations

There are many existing opensource encrypted messaging system.
Here is a list of downsides from existing secure messaging systems.

### Why not Signal

Signal takes many measures to protect its users, such as [cryptographic deniability](https://www.praetorian.com/blog/an-opinionated-series-on-why-signal-protocol-is-well-designed-deniability/) and [forward secrecy](https://signal.org/blog/asynchronous-security/), and is known for [not having access to the users' messages](https://www.youtube.com/watch?v=3oPeIbpA5x8).

However, Signal relies on centralized servers, which can be compromised at some point. These servers can try to deanonimize the users with their IP address, and already know their phone numbers, since Signal requires one to register.
This phone number can be used to [track the device](https://en.wikipedia.org/wiki/Mobile_phone_tracking) and its owner at any time, and retroactively. This means that even if no one can read your messages on Signal, your physical identity can be retrieved and your phone (or computer) can be seized.

Due to the centralized nature of Signal, the need for a phone number to register cannot be fixed. While it is possible to use a burner phone and bypass the phone number restriction, I don't think Signal should require it in the first place.

Additionally, the Signal codebase is very large. This makes Signal slow to audit, and impossible to fork. One of the design principles of Colibri is to be simple enough that anyone can audit the cryptographic part.

### Why not Matrix

Unlike Signal, Matrix uses a decentralized protocol, can be used from an anonymous web browser with an anonymous internet access without registering a phone number, and can be self hosted relatively easily.

There are two ways to use Matrix: either by hosting one's own server, or by registering an account on someone else's.
In order to host a private Matrix server, one has to register a domain name, which is usually incompatible with privacy because having a domain requires a credit card.
However, by using someone else's server, the owner of the server has access to all the metadata that concerns your communications: which public servers you joined, when you last talked to someone, changed avatar,...

While using someone else's server can be compatible with anonymity, using the same account and keeping privacy is not possible in the long term. Moreover, the encryption is only useful for rooms that are not public, and deniability is not possible when the entire history is stored on the server.

Colibri is designed against long-lived identities. Each communication requires creating a new identity, accross all the existing servers. This design makes it impossible for any server to control or track a user's identity.

Additionally, Colibri is intended for portable deployment. In practice, this means anyone anywhere can easily run a Colibri server on Tor or I2P, or even under a subfolder of an existing website.
The only requirement for users to use these Colibri instances is to be able to contact the server.

For example, any of the URL could host a Colibri server instance:
```
lbxty5d7w3mjzqow4ta2f5wjhv6kpuwa6rwn5coeomsva4ydagcoiyd.onion
https://theartofmonero.com/secret-colibri
https://colibri.theartofmonero.com
http://localhost:8000
```
The first URL can only be accessed through Tor (with Whonix for example), and the last one can only be accessed on the local computer.
The second URL could be used to hide the existence of a Colibri instance with a dummy website and SSL encryption.

What I mean with these examples is that Colibri has no requirement on its own, and tries to stay as small as possible.
If you look at the current source code of the server, the entire codebase is about 326 lines (the client is larger because it has to manage encryption and CLI commands, but we are still under 3K).



### Why Colibri

I believe Colibri also has unique advantages and objectives over other secure messaging services, due to its minimalism:
- Easy to audit (any developper should be able to do so)
- Can be hosted anywhere
- The user experience comes from the security choices (deniability, forward secrecy and identity management are part of the user experience)
- third parties, including servers, should not be able to know who communicates with whom


## Protocol

See [PROTOCOL.md](./PROTOCOL.md) for the protocol details.

## How to use

The server (node) is where users register new addresses and store their chat history. It can be ran in any configuration, as long as the end user can connect to the server.
To setup your own server: see [the server readme](./server/)

The CLI client is a low level python script to interact with the server and with other users.
To install the CLI client: see [the cli client readme](./cli-client/).

[//]: # "## Future plans"
[//]: # ""
[//]: # "These ideas will not be considered until the base service works."
[//]: # ""
[//]: # "- In order to improve the reactivity, the server and CLI client will probably need some kind of event streaming feature to allow the server to send events to the client."
[//]: # "- Some additional features, like bridges, will have to be implemented as external bots in order to keep the code base small."
[//]: # "To do this, a special type of message could be created to allow custom extensions to exchange data."
[//]: # ""

