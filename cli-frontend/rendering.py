import sys
import time
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


# print(ctl.style(italic, underline, fg_bright(red)) + "test" + ctl.style(reset))

rows = 24
cols = 80

# basic state "management"
# TODO: refactor

tabs = {
    "servers": "servers (S)",
    "rooms": "rooms (R)",
    "addresses": "addresses (A)",
    "broadcasts": "broadcasts (B)",
}
selected = "servers"


def titles():
    # print categories: server, addresses, rooms and broadcasts
    for i, tab in enumerate(tabs):
        ctl.move(1 + 20 * i, 1)
        if selected == tab:
            ctl.style(reset, underline, fg_bright(cyan))
        else:
            ctl.style(reset, fg(cyan))
        print(tabs[tab])

def refresh():
    ctl.clear()
    titles()
    # sys.stdout.flush()
    time.sleep(1 / 30)
