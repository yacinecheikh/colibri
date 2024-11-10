from ansi_lib.colors import (
    reset,
    fg_reset,
    bg_reset,

    bold,
    italic,
    underline,

    # basic palette
    black,
    red,
    green,
    yellow,
    blue,
    magenta,
    cyan,
    white,

    # functions
    fg_bright,
    bg_bright,
    fg,
    bg,
    fg_256,
    bg_256,
    # fg_rgb,
    # bg_rgb,
)
from ansi_lib import ctl


print(ctl.style(italic, underline, fg_bright(red)) + "test" + ctl.style(reset))
# clear command
#print(clear() + move(1, 1), end="")

term_state = ctl.get_terminal_state()
term_size = ctl.get_size()
print(term_size)


def cleanup():
    print("cleanup")
    ctl.restore_buffer()
    ctl.show_cursor()
    ctl.set_terminal_state(term_state)
    ctl.set_size(*term_size)

    """
    end = datetime.now()
    dt = end - start
    dt = float(dt.seconds) + float(dt.microseconds) / 1000000
    framerate = loops / dt
    print(f"time: {dt}")
    print(f"framerate: {framerate}")
    """
    # do not use sys.exit()
    # sys.exit() can report a SystemExit exception
    import os
    os._exit(0)


def init():
    ctl.save_buffer()
    ctl.hide_cursor()
    ctl.no_echo()
    ctl.disable_line_buffering()
    ctl.set_nonblocking()
    ctl.set_size(24, 80)

    ctl.clear()
    # flush manually because flushing is not done automatically without \n
    # TODO: add flush=True to every ctl command
    print("", end="", flush=True)


print(ctl.get_size())
ctl.on_cleanup(cleanup)
# ctl.on_resize(resize)
init()
print(ctl.move(1, 1), end="")


# from datetime import datetime


# start = datetime.now()
# loops = 0
while True:
    try:
        ch = ctl.getch()
        if ch == "q":
            break
        elif ch == "g":
            print(ctl.get_size())
        elif ch:
            print(repr(ch))
        # loops += 1
    except EOFError:
        pass
    except Exception as e:
        print(e)
