# View-specific DOM widgets

import dom


class Tabs(dom.Node):
    def __init__(self):
        self.tabs = [
            # servers
            dom.Text("servers (S)", color=dom.colors.cyan),
            # rooms
            dom.Text("rooms (R)", color=dom.colors.cyan),
            # addresses
            dom.Text("addresses (A)", color=dom.colors.cyan),
            # broadcasts
            dom.Text("broadcasts (B)", color=dom.colors.cyan),
        ]
        self.selected = 0
        self.tabs[0].highlighted = True
        self.events = ["\x1b[D", "\x1b[C"]

    def on_event(self, key, data):
        if key == "\x1b[D":
            self.tabs[self.selected].highlighted = False
            self.selected = (self.selected - 1) % len(self.tabs)
            self.tabs[self.selected].highlighted = True
        elif key == "\x1b[C":
            self.tabs[self.selected].highlighted = False
            self.selected = (self.selected + 1) % len(self.tabs)
            self.tabs[self.selected].highlighted = True

    def render(self, x, y):
        for i, tab in enumerate(self.tabs):
            tab.render(1 + 20 * i, y)
