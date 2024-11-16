"""
DOM-like widget API

Pure logic dom (does not manage rendering)
"""

from ansi_lib import ctl
from ansi_lib import colors
from ansi_lib import keys
import dom
from dom import Box, Text


# state store/reference type
# simplifies states management by isolating mutability
# and makes signal-based re-rendering possible
class ref:
    def __init__(self, value):
        self._value = value
        self.callbacks = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        for callback in self.callbacks:
            callback()

    def watch(self, callback):
        self.callbacks.append(callback)


# "futures"
# lazy loaded globals, alternative to recursive reference passing
document_ref = ref(None)
get_document = lambda: document_ref.value



class UI:
    def __init__(self):
        # the display is permanent (lifetime is equal to self)
        # this is needed for focus and other external references
        self.display = Box()

    def load(self):
        self.tabselector = TabSelector()
        #self.inputviewer = InputViewer()
        # can define key callbacks on self.display here

        self.refresh_display()

        # manually define the document root and focus
        doc = get_document()
        doc.root.contents = self.display
        # this will trigger tabselector.display.on_focus and rerender
        doc.selected = self.tabselector.display

        #doc.selected = self.inputviewer.display


    def refresh_display(self):
        # onkey events can also be attached to the display itself
        # this makes them permanent
        self.display.contents = dom.Group(None, onkey={
            "q": self.on_quit,
        })
        self.display.contents.add(self.tabselector.display)
        #self.display.contents.add(self.inputviewer.display)
        # attach children to the current block (not the permanent Box wrapper) to allow key event propagation
        self.tabselector.display.parent = self.display.contents
        #self.inputviewer.display.parent = self.display.contents

    def on_quit(self):
        import sys
        sys.exit(0)
    #def on_key(self, key):
    #    if key == "q":
    #        import sys
    #        sys.exit()
    #        return True
    #    # no upper parent to bubble the event


    #def on_event(self, name, data):
    #    if name == "key" and data == "q":
    #        import sys
    #        sys.exit(0)




# exploratory widget
# used to figure out what strings special keys are represented by
class InputViewer:
    def __init__(self):
        self.buffer = ""
        self.display = Box()
        self.display.key_callbacks["any"] = self.on_key

        self.refresh_display()
    
    def refresh_display(self):
        self.display.contents = Text(self.display, repr(self.buffer), color=colors.white)

    def on_key(self, key):
        self.buffer += key
        self.refresh_display()


class TabSelector:
    def __init__(self):
        self.tabs = [
            "servers (S)",
            "rooms (R)",
            "addresses (A)",
            "broadcasts (B)",
        ]
        self.selected = ref(0)

        self.display = Box()
        self.display.focus_callback = self.refresh_display
        self.display.key_callbacks[keys.left] = lambda: self.on_event("left")
        self.display.key_callbacks[keys.right] = lambda: self.on_event("right")
        self.display.key_callbacks["s"] = lambda: self.on_event("set", 0)
        self.display.key_callbacks["r"] = lambda: self.on_event("set", 1)
        self.display.key_callbacks["a"] = lambda: self.on_event("set", 2)
        self.display.key_callbacks["b"] = lambda: self.on_event("set", 3)
        self.refresh_display()

    def on_event(self, name, data=None):
        if name == "left":
            self.selected.value = (self.selected.value - 1) % len(self.tabs)
        elif name == "right":
            self.selected.value = (self.selected.value + 1) % len(self.tabs)
        elif name == "set":
            self.selected.value = data
        else:
            raise ValueError(f"unknown event type: {name}")

        self.refresh_display()

    def refresh_display(self):
        group = dom.Group(parent=None)
        tab_labels = []
        for tab in self.tabs:
            tab_labels.append(dom.Text(group, tab, color=colors.cyan))
        tab_labels[self.selected.value].highlighted = True
        for i, label in enumerate(tab_labels):
            label.hitbox.x = 1 + 20 * i
            group.add(label)
        self.display.contents = group
    
