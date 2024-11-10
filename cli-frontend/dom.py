"""
DOM-like widget API
"""

from ansi_lib import ctl
from ansi_lib import colors


class Node:
    # default values for nodes that do not use them
    events = []
    children = []

    def render(self, x, y):
        raise NotImplementedError

    def on_event(self, key, data):
        raise NotImplementedError


class Document:
    def __init__(self, root):
        self.root = root
        self.event_handlers = self.index_event_handlers(root)

    def index_event_handlers(self, node):
        event_handlers = {}
        for event in node.events:
            event_handlers[event] = node
        for child in node.children:
            event_handlers.update(self.index_event_handlers(child))
        return event_handlers

    def emit_event(self, event, event_data):
        if event in self.event_handlers:
            self.event_handlers[event].on_event(event, event_data)
        else:
            raise Exception(f"Event {event} not handled")

    def render(self):
        self.root.render(1, 1)


# concrete Node classes
class Text(Node):
    def __init__(self, text, *styles, color=None, highlighted=False):
        self.text = text
        self.styles = styles
        # dynamic styling (ad-hoc requirement)
        self.highlighted = highlighted
        self.color = color

    def render(self, x, y):
        ctl.move(x, y)
        ctl.style(colors.reset, *self.styles)
        if self.highlighted:
            ctl.style(colors.fg_bright(self.colors))
        print(self.text)


class PositionOffset(Node):
    def __init__(self, node, x, y):
        self.node = node
        self.x = x
        self.y = y

    def render(self, x, y):
        self.node.render(x + self.x, y + self.y)


class List(Node):
    def __init__(self, children):
        self.children = children

    def render(self, x, y):
        for i, item in enumerate(self.children):
            item.render(x, y + i)
