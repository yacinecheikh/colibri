import os
import sys


if not os.path.exists('data'):
    os.mkdir('data')

from errno import *
from stat import *
import fcntl
from threading import Lock
# pull in some spaghetti to make this stuff work without fuse-py being installed
import fuse
from fuse import Fuse


fuse.fuse_python_api = (0, 2)

fuse.feature_assert('stateful_files', 'has_init')

def print(x):
    with open("/home/yacine/colibri/client/log.txt", "a") as f:
        f.write(str(x))
        f.write("\n")


def flag2mode(flags):
    md = {os.O_RDONLY: 'rb', os.O_WRONLY: 'wb', os.O_RDWR: 'wb+'}
    m = md[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

    if flags | os.O_APPEND:
        m = m.replace('w', 'a', 1)

    return m


class Xmp(Fuse):

    def __init__(self, *args, **kw):
        print("initing Xmp")
        #print(f"args: {args}, {kw}")

        Fuse.__init__(self, *args, **kw)

        # TODO: do stuff to set up your filesystem here, if you want
        self.root = '/'

    def getattr(self, path):
        print(f"getattr {path}")
        print(os.lstat("." + path))
        return os.lstat("." + path)

    def readlink(self, path):
        print(f"readlink {path}")
        # os.readlink(symlink) -> realpath
        print(os.readlink("." + path))
        return os.readlink("." + path)

    def readdir(self, path, offset):
        print(f"readdir {path} with offset {offset}")
        print(os.listdir("." + path))
        for e in os.listdir("." + path):
            yield fuse.Direntry(e)

    def fsinit(self):
        print("fsinit")
        #print(f"chdir {self.root}")
        os.chdir(self.root)

    class KeyFile:
        def __init__(self, path, flags, *mode):
            print(f'opened file {path} with flags {flags} and mode {mode}')
            # TODO: load key
            self.path = path

        def read(self, length, offset):
            print(f'reading {self.path} at {offset} for {length}')
            text = "x" * length
            # file size is 250 -> truncate
            excess = length + offset - 250
            return text[:-excess]

        def write(self, buf, offset):
            # TODO: test
            # never write
            return 0
            #return os.pwrite(self.fd, buf, offset)

        def release(self, flags):
            pass
            #self.file.close()

        def _fflush(self):
            if 'w' in self.file.mode or 'a' in self.file.mode:
                self.file.flush()

        def fsync(self, isfsyncfile):
            self._fflush()
            if isfsyncfile and hasattr(os, 'fdatasync'):
                os.fdatasync(self.fd)
            else:
                os.fsync(self.fd)

        def flush(self):
            self._fflush()
            # cf. xmp_flush() in fusexmp_fh.c
            os.close(os.dup(self.fd))

        def fgetattr(self):
            #return os.fstat(self.fd)
            return 

    class XmpFile(object):

        def __init__(self, path, flags, *mode):
            print("initing file")
            print(f'opened file {path} with flags {flags} and mode {mode}')
            self.file = os.fdopen(os.open("." + path, flags, *mode),
                                  flag2mode(flags))
            print(f"file: {self.file}")
            self.fd = self.file.fileno()
            print(f"fd: {self.fd}")
            self.iolock = None
            #if hasattr(os, 'pread'):
            #    self.iolock = None
            #    print(f"os hasattr pread")
            #else:
            #    self.iolock = Lock()
            #    print("lock")

        def read(self, length, offset):
            print(f"read {length} {offset}")
            #if self.iolock:
            #    self.iolock.acquire()
            #    try:
            #        self.file.seek(offset)
            #        return self.file.read(length)
            #    finally:
            #        self.iolock.release()
            #else:
            return os.pread(self.fd, length, offset)

        def write(self, buf, offset):
            print(f"write {buf} {offfset}")
            #if self.iolock:
            #    self.iolock.acquire()
            #    try:
            #        self.file.seek(offset)
            #        self.file.write(buf)
            #        return len(buf)
            #    finally:
            #        self.iolock.release()
            #else:
            return os.pwrite(self.fd, buf, offset)

        def release(self, flags):
            print(f"release {flags}")
            self.file.close()

        def _fflush(self):
            print("fflush")
            if 'w' in self.file.mode or 'a' in self.file.mode:
                self.file.flush()

        def fsync(self, isfsyncfile):
            print(f"fsync {isfsyncfile}")
            self._fflush()
            if isfsyncfile and hasattr(os, 'fdatasync'):
                print("os has fdatasync")
                os.fdatasync(self.fd)
            else:
                os.fsync(self.fd)

        def flush(self):
            print("flush")
            self._fflush()
            # cf. xmp_flush() in fusexmp_fh.c
            print("closing a duplicate of fd")
            os.close(os.dup(self.fd))

        def fgetattr(self):
            print("fgetattr")
            print(os.fstat(self.id))
            return os.fstat(self.fd)

        def ftruncate(self, len):
            print("ftruncate")
            self.file.truncate(len)

        def lock(self, cmd, owner, **kw):
            print(f"lock {cmd} {owner} {kw}")
            # The code here is much rather just a demonstration of the locking
            # API than something which actually was seen to be useful.

            # Advisory file locking is pretty messy in Unix, and the Python
            # interface to this doesn't make it better.
            # We can't do fcntl(2)/F_GETLK from Python in a platfrom independent
            # way. The following implementation *might* work under Linux.
            #
            # if cmd == fcntl.F_GETLK:
            #     import struct
            #
            #     lockdata = struct.pack('hhQQi', kw['l_type'], os.SEEK_SET,
            #                            kw['l_start'], kw['l_len'], kw['l_pid'])
            #     ld2 = fcntl.fcntl(self.fd, fcntl.F_GETLK, lockdata)
            #     flockfields = ('l_type', 'l_whence', 'l_start', 'l_len', 'l_pid')
            #     uld2 = struct.unpack('hhQQi', ld2)
            #     res = {}
            #     for i in xrange(len(uld2)):
            #          res[flockfields[i]] = uld2[i]
            #
            #     return fuse.Flock(**res)

            # Convert fcntl-ish lock parameters to Python's weird
            # lockf(3)/flock(2) medley locking API...
            print(f"F_UNLCK: {fcntl.F_UNLCK}")
            print(f"f_rdlck: {fcntl.F_RDLCK}")
            print(f"f_wrlck: {fcntl.F_WRLCK}")
            op = { fcntl.F_UNLCK : fcntl.LOCK_UN,
                   fcntl.F_RDLCK : fcntl.LOCK_SH,
                   fcntl.F_WRLCK : fcntl.LOCK_EX }[kw['l_type']]
            print(f"op: {op}")
            print(f"kw(l_type): {kw}")
            print(op)
            if cmd == fcntl.F_GETLK:
                print("-EOPNOTSUPP")
                return -EOPNOTSUPP
            elif cmd == fcntl.F_SETLK:
                if op != fcntl.LOCK_UN:
                    op |= fcntl.LOCK_NB
                    print("op |= fcntl.LOCK_NB")
                    print(f"op: {op}")
            elif cmd == fcntl.F_SETLKW:
                pass
            else:
                print("-EINVAL")
                return -EINVAL

            print(f"fcntl.lockf(fd, {op}, {kw['l_start']}, {kw['l_len']})")
            fcntl.lockf(self.fd, op, kw['l_start'], kw['l_len'])


    def main(self, *a, **kw):

        self.file_class = self.XmpFile
        #self.file_class = self.KeyFile

        return Fuse.main(self, *a, **kw)


def main():

    usage = """
Userspace nullfs-alike: mirror the filesystem tree from some point on.

""" + Fuse.fusage

    server = Xmp(version="%prog " + fuse.__version__,
                 usage=usage,
                 dash_s_do='setsingle')

    server.parser.add_option(mountopt="root", metavar="PATH", default='/',
                             help="mirror filesystem from under PATH [default: %default]")
    server.parse(values=server, errex=1)

    # enter root of underlying filesystem
    if server.fuse_args.mount_expected():
        os.chdir(server.root)

    server.main()


if __name__ == '__main__':
    main()

