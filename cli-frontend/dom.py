"""
Rendering API

HTML-like recursive hierarchy of graphical objects (text, hitbox,...)
"""
import sys
import time
from ansi_lib import colors
"""
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
"""
from ansi_lib import ctl


# TODO: add support for clicks
class HitBox:
    def __init__(self, x, y, w=1, h=1):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Node:
    # parent is used to bubble events ?
    # (shuld also use the logic tree for event interception)
    def __init__(self, parent, x=0, y=0, w=1, h=1, onclick=None, onkey=None, onfocus=None):
        self.parent = parent
        self.children = []
        self.hitbox = HitBox(x, y, w, h)
        self.click_callback = onclick
        self.key_callbacks = onkey or {}
        self.focus_callback = onfocus
        self.selected = False  # focus management, set to True when document.selected = <self>

    def render(self, x, y):
        pass
        #raise NotImplementedError

    def capture_click(self, x, y):
        # TODO: use hitboxes and .children to find which child node was clicked, or call self.on_click(x, y)
        # TODO: be careful of relative positioning (hitboxes must have absolute positions)
        raise NotImplementedError

    def on_click(self, x, y):
        # TODO: call parent.on_click(x, y) if self.click_callback is None
        raise NotImplementedError

    def on_key(self, key):
        # propagate (bubble up) to parent.on_key(key) if self.key_callbacks[key] is not defined
        if key in self.key_callbacks:
            self.key_callbacks[key]()
        elif self.parent is not None:
            self.parent.on_key(key)
    
    def on_focus(self):
        if self.focus_callback is not None:
            self.focus_callback()


# Rendering and user event manager
class Document:
    def __init__(self):
        self.root = Box(None)
        self._selected = self.root

    def init(self, root, selected):
        self.root = root
        self.selected = selected

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self._selected.selected = False
        self._selected = value
        self._selected.selected = True
        self._selected.on_focus()

    def render(self):
        self.root.render(1, 1)

    # key press events bubble up from the currently focused element
    def on_key(self, key):
        self.selected.on_key(key)

    # mouse click events are captured by the deepest element before bubbling up
    def on_click(self, x, y):
        self.root.capture_click(x, y)



# Ad-hoc components
# (no generic Div, Text or Box for now)
class Text(Node):
    def __init__(self, parent, text, *styles, color=colors.white, highlighted=False):
        super().__init__(parent)
        self.text = text
        self.styles = styles
        # dynamic styling (ad-hoc requirement)
        self.highlighted = highlighted
        self.color = color
        # TODO: make sure there is no newline when rendering, this will break the hitbox
        # OR: implement fixed-size boxes (too complex, no)
        self.hitbox.w = len(text)

    def render(self, x, y):
        ctl.move(x + self.hitbox.x, y + self.hitbox.y)
        ctl.style(colors.reset, *self.styles)
        if self.highlighted:
            ctl.style(colors.fg_bright(self.color))
        else:
            ctl.style(colors.fg(self.color))
        print(self.text)


class Group(Node):
    def add(self, elt):
        self.children.append(elt)

    def render(self, x, y):
        for elt in self.children:
            elt.render(x + self.hitbox.x, y + self.hitbox.y)


# lazy linked Node
class Box(Node):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.children.append(Node(self))

    @property
    def contents(self):
        #assert self.children[0] is not None
        return self.children[0]

    @contents.setter
    def contents(self, value):
        self.children[0] = value

    def render(self, x, y):
        self.contents.render(x, y)

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
