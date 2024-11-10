import sys
import os
import fcntl
import termios
import atexit
import signal


def style(*modifiers):
    return '\033[{}m'.format(';'.join(map(str, modifiers)))


def color(text, color):
    return f'\033[{color}m{text}\033[0m'


# absolute move
def move(x, y):
    return f'\033[{y};{x}H'


def move_x(x):
    return f'\033[{x}G'


def move_y(y):
    return f'\033[{y}d'


# clear screen
def clear():
    print('\033[2J', end="")


# clear line
def clear_line():
    return '\033[K'


# cursor
def hide_cursor():
    print('\033[?25l', end="")


def show_cursor():
    print('\033[?25h', end="")


# switch to alternate buffer
def save_buffer():
    print('\033[?1049h', end="")


# switch to normal buffer
def restore_buffer():
    clear()
    print('\033[?1049l', end="")


def save_cursor():
    return '\033[s'


def restore_cursor():
    return '\033[u'


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


# prevent stdin from buffering with fcntl
# TODO: try to remove unneeded flags
def set_nonblocking():
    # allow reading without blocking (raise EOFError)
    flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
    # disable buffering ?
    flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, flags | os.O_NDELAY)


# read a key event from stdin
def getch():
    return sys.stdin.read(1)


def on_resize(func):
    def callback(sig, frame):
        # get terminal size
        winsize = termios.tcgetwinsize(sys.stdout.fileno())
        func(*winsize)
    signal.signal(signal.SIGWINCH, callback)


def on_cleanup(cleanup):
    atexit.register(cleanup)
    """
    def callback(sig, frame):
        cleanup()
    signal.signal(signal.SIGINT, callback)
    signal.signal(signal.SIGTERM, callback)
    """
