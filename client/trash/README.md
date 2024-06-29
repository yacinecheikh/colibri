# Trash

Unused files that may be useful to someone someday

# Dropped projects

## LUKS-based data store encryption, in a namespace

This system would allow a process to mount a dynamic LUKS volume (thanks to Qemu virtual disks and qemu-nbd), and only allow a single process tree to access it

The problem with this solution is that:
- it is not simple
- it requires root access
- other tools exist to reproduce this level of security

files: init.sh, start.sh, requirements

## FUSE proxy for GPG keys stored in a database

This system has similar motivations as the LUKS mount namespace, but can be done without being root

Unfortunately, this is bloated and people who can use encryption already do it.

The system itself having a malware (root or not) is currently not protected agaist. If you want this level of security, use a system that is isolated in the first place (Tails, QubesOS, Whonix,...), encrypt it and keep the data disconnected when not using it.

files: fs.py, init\_db.sql, requirements.txt
