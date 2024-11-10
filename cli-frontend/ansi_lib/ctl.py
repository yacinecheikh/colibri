import sys
import os
import fcntl
import termios
import atexit
import signal


# def color(text, color):
#    return f'\033[{color}m{text}\033[0m'


def do(ansi_code):
    print(ansi_code, end="", flush=True)


def style(*modifiers):
    do('\033[{}m'.format(';'.join(map(str, modifiers))))
    # return '\033[{}m'.format(';'.join(map(str, modifiers)))


# def write(text):
#    print(text, end="", flush=True)


# absolute move
def move(x, y):
    do(f'\033[{y};{x}H')


def move_x(x):
    do(f'\033[{x}G')


def move_y(y):
    do(f'\033[{y}d')


def get_size():
    rows, cols = termios.tcgetwinsize(sys.stdout.fileno())
    return rows, cols


def set_size(rows, cols):
    do(f"\x1b[8;{rows};{cols}t")


# clear screen
def clear():
    do('\033[2J')


# clear line
def clear_line():
    do('\033[K')


# cursor
def hide_cursor():
    do('\033[?25l')


def show_cursor():
    do('\033[?25h')


# switch to alternate buffer
def save_buffer():
    do('\033[?1049h')


# switch to normal buffer
def restore_buffer():
    clear()
    do('\033[?1049l')


# not used
def save_cursor():
    do('\033[s')


def restore_cursor():
    do('\033[u')


# termios state
def get_terminal_state():
    return [termios.tcgetattr(sys.stdin.fileno()),
            termios.tcgetattr(sys.stdout.fileno())]


def set_terminal_state(state):
    stdin_state, stdout_state = state
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, stdin_state)
    termios.tcsetattr(sys.stdout.fileno(), termios.TCSANOW, stdout_state)


def no_echo():
    state = termios.tcgetattr(sys.stdin.fileno())
    state[3] &= ~termios.ECHO
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, state)


"""
def no_buffering():
    state = termios.tcgetattr(sys.stdin.fileno())
    state[3] &= ~termios.ICANON
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, state)
"""


def disable_line_buffering():
    import tty
    tty.setcbreak(sys.stdin.fileno())
    # tty.setcbreak(sys.stdout.fileno())


# TODO: use PYTHONUNBUFFERED=1 instead
# makes stdin non-blocking (buggy if stdout is blocking, will randomly raise BlockingIOError)
"""
# prevent stdin from buffering with fcntl
# TODO: try to remove unneeded flags
def set_nonblocking():
    # allow reading without blocking (raise EOFError)
    flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
    # disable buffering ?
    flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, flags | os.O_NDELAY)

    # does not solve the BlockingIOError problem
    # flags = fcntl.fcntl(sys.stdout.fileno(), fcntl.F_GETFL)
    # fcntl.fcntl(sys.stdout.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
    # flags = fcntl.fcntl(sys.stdout.fileno(), fcntl.F_GETFL)
    # fcntl.fcntl(sys.stdout, fcntl.F_SETFL, flags | os.O_NDELAY)
"""


# read a key event from stdin
def getch():
    return sys.stdin.read(1)


def on_resize(func):
    def callback(sig, frame):
        # get terminal size
        winsize = termios.tcgetwinsize(sys.stdout.fileno())
        func(*winsize)
    signal.signal(signal.SIGWINCH, callback)


"""
def resize(x, y):
    print(x, y)
on_resize(resize)
"""


def on_cleanup(cleanup):
    atexit.register(cleanup)
    """
    def callback(sig, frame):
        cleanup()
    signal.signal(signal.SIGINT, callback)
    signal.signal(signal.SIGTERM, callback)
    """
