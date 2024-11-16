#!/usr/bin/env PYTHONUNBUFFURED=1 python3
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
import dom
import view


# fail-safe print if PYTHONUNBUFFERED=1 is missing
# builtin_print = print
# def my_print(*args, **kwargs):
#     try:
#         builtin_print(*args, **kwargs)
#     except BlockingIOError as e:
#         print(e)
# import builtins
# builtins.print = my_print


# initial terminal state (restored after running the program)
term_state = ctl.get_terminal_state()
term_size = ctl.get_size()


# constants
size = 24, 80


def cleanup():
    # print("cleanup")
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
    ctl.set_size(*size)
    ctl.move(1, 1)

    ctl.clear()


ctl.on_cleanup(cleanup)
init()


def main():
    # text = dom.Text("Hello world!", color=cyan, highlighted=True)
    # keyviewer = dom.Text("", color=cyan)
    # keyviewer.buffer = ""

    # user-centric UI
    document = dom.Document()
    # create the app UI logic manager
    ui = view.UI()
    # make the document available to all UI components (needed for focus management)
    view.document_ref.value = document
    # generate the user interface logic
    ui.load()
    # display the UI
    #document.set_root(ui.display)
    #v = view.View(view.UI())

    while True:
        #v.render()
        document.render()
        ch = ctl.getch()
        if ch == "":
            continue
        # TODO: parse mouse click events
        else:
            document.on_key(ch)
        #elif ch == "q":
        #    break
        #else:
        #    doc.emit_event(ch, None)
        # else:
            # keyviewer.buffer += ch
            # keyviewer.text = repr(keyviewer.buffer)


try:
    main()
except Exception as e:
    import traceback
    with open("error", "w") as f:
        traceback.print_exception(e, file=f)
        #f.write(repr(e))
