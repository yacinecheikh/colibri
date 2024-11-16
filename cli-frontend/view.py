"""
DOM-like widget API

Pure logic dom (does not manage rendering)
"""

from ansi_lib import ctl
from ansi_lib import colors
import dom


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
        self.tabselector = TabSelector()
        # WARNING
        # The UI must never be refreshed after that
        # (or the Document will be entirely desynchronized with the new UI)
        self.refresh_display()


        # manually define the document root and focus
        doc = get_document()
        doc.init(self.display, self.tabselector.display)
        # rendering changes when focused
        # TODO: use signals to let tabselector get notified when the focus goes to its display
        self.tabselector.on_focus()

    def refresh_display(self):
        self.display = dom.Group(None, onkey={
            "q": self.on_quit,
        })
        self.display.add(self.tabselector.display)
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
        group = dom.Group(parent=None)
        tab_labels = []
        for tab in self.tabs:
            tab_labels.append(dom.Text(group, tab, color=colors.cyan))
        tab_labels[self.selected.value].highlighted = True
        for i, label in enumerate(tab_labels):
            label.hitbox.x = 1 + 20 * i
            group.add(label)
        self.display = group
