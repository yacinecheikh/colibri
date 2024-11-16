"""
DOM-like widget API

Pure logic dom (does not manage rendering)
"""

from ansi_lib import ctl
from ansi_lib import colors
import dom
from dom import Box


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
        self.tabselector.display.parent = self.display  # attach child
        # can define key callbacks on self.display here

        self.refresh_display()
        # manually define the document root and focus
        doc = get_document()
        doc.root.contents = self.display
        # this will trigger tabselector.display.on_focus and rerender
        doc.selected = self.tabselector.display


    def refresh_display(self):
        # onkey events can also be attached to the display itself
        # this makes them permanent
        self.display.contents = dom.Group(None, onkey={
            "q": self.on_quit,
        })
        self.display.contents.add(self.tabselector.display)
        self.tabselector.display.parent = self.display

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
        self.display.focus_callback = self.on_focus
        self.refresh_display()

    def on_event(self, name, data):
        if name == "left":
            self.selected.value = (self.selected - 1) % len(self.tabs)
        elif name == "right":
            self.selected.value = (self.selected + 1) % len(self.tabs)
        else:
            raise ValueError(f"unknown event type: {name}")

        self.refresh_display()

    def on_focus(self):
        self.refresh_display()

    def refresh_display(self):
        # the parent of the display is set externally
        #if self.display.selected:
        #    print("\ntest")
        group = dom.Group(parent=None)
        tab_labels = []
        for tab in self.tabs:
            tab_labels.append(dom.Text(group, tab, color=colors.cyan))
        tab_labels[self.selected.value].highlighted = True
        for i, label in enumerate(tab_labels):
            label.hitbox.x = 1 + 20 * i
            group.add(label)
        self.display.contents = group
    
