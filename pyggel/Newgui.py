"""
pyggle.gui
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The gui module contains classes to create and use a simple Graphical User Interface.
"""

from include import *
import image, view, font, event
import time

class Packer(object):
    def __init__(self, app=None, packtype="wrap", width=10):
        self.app = app
        self.packtype = packtype
        self.width = width

        self.need_to_pack = False

    def pack(self):
        getattr(self, "pack_%s"%self.packtype)()
        self.need_to_pack = False

    def pack_wrap(self):
        nw = 0
        nh = 0
        newh = 0

        self.app.widgets.reverse()

        for i in self.app.widgets:
            if isinstance(i, NewLine):
                nx = 0
                nh += newh + i.height
                newh = 0
                continue
            if i.override_pos:
                continue
            w, h = i.size
            if nw + w > self.width and nw:
                nh += newh + 1
                newh = h
                nw = w
                pos = (0, nh)
            else:
                pos = (nw, nh)
                nw += w
                if h > newh:
                    newh = h
            i.force_pos_update(pos)
        self.app.widgets.reverse()

class App(object):
    """A simple Application class, to hold and control all widgets."""
    def __init__(self, event_handler):
        """Create the App.
           event_handler must be the event.Handler object that the gui will use to get events,
           and each event handler may only have on App attached to it."""
        self.event_handler = event_handler
        self.event_handler.gui = self

        self.widgets = []

        self.dispatch = event.Dispatcher()
        self.dispatch.bind("new-widget", self.new_widget)

        self.mefont = font.MEFont()
        self.regfont = font.Font()

        self.packer = Packer(self, width=view.screen.screen_size[0])

        self.visible = True

    def get_mouse_pos(self):
        """Return mouse pos based on App position - always (0,0)"""
        return view.screen.get_mouse_pos()

    def new_widget(self, widget):
        """Add a new widget to the App."""
        if not widget in self.widgets:
            self.widgets.insert(0, widget)
            if not widget.override_pos:
                self.packer.need_to_pack = True

    def handle_mousedown(self, button, name):
        """Callback for mouse click events from the event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_mousedown(button, name):
                    return True
        return False
    def handle_mouseup(self, button, name):
        """Callback for mouse release events from the event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_mouseup(button, name):
                    return True
        return False
    def handle_mousehold(self, button, name):
        """Callback for mouse hold events from the event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_mousehold(button, name):
                    return True
        return False

    def handle_uncaught_event(self, event):
        """Callback for uncaught_event events from event_handler."""
        if event.type == MOUSEMOTION:
            if "left" in self.event_handler.mouse.active:
                return self.handle_drag(event)
        else:
            for i in self.widgets:
                if i.visible:
                    if i.handle_uncaught_event(event):
                        return True
        return False

    def handle_drag(self, event):
        """Callback for mouse drag events."""
        for i in self.widgets:
            if i.handle_drag(event):
                return True
        return False

    def handle_keydown(self, key, string):
        """Callback for key press events from event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_keydown(key, string):
                    return True
        return False

    def handle_keyup(self, key, string):
        """Callback for key release events from event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_keyup(key, string):
                    return True
        return False

    def handle_keyhold(self, key, string):
        """Callback for key hold events from event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_keyhold(key, string):
                    return True
        return False

    def next_widget(self):
        """Cycle widgets so next widget is top one."""
        self.widgets.append(self.widgets.pop(0))
        while not self.widgets[0].visible:
            self.widgets.append(self.widgets.pop(0))

    def set_top_widget(self, widg):
        """Moves widget 'widg' to top position."""
        if widg in self.widgets:
            self.widgets.remove(widg)
        self.widgets.insert(0, widg)

    def render(self, camera=None):
        """Renders all widgets, camera can be None or the camera object used to render the scene."""
        self.widgets.reverse()
        for i in self.widgets:
            if i.visible: i.render()
        self.widgets.reverse()

class Widget(object):
    def __init__(self, app, pos=None):
        self.app = app
        self.pos = pos
        self.size = (0,0)
        if pos:
            self.override_pos = True
        else:
            self.override_pos = False

        self.dispatch = event.Dispatcher()

        self.visible = True
        self.app.dispatch.fire("new-widget", self)
        self.image = None

        self._mdown = False
        self.key_active = True
        self.key_hold_lengths = {}
        self.khl = 100 #milliseconds to hold keys for repeat!

    def pack(self):
        self.app.packer.pack()

    def _collidem(self):
        x, y = self.app.get_mouse_pos()
        a, b = self.pos
        w, h = self.size
        return (x >= a and x <= a+w) and (y >= b and y <= b+h)

    def handle_mousedown(self, button, name):
        if name == "left":
            if self._collidem():
                self._mdown = True
                self.dispatch.fire("mousedown")
                return True

    def handle_mouseup(self, button, name):
        if name == "left":
            if self._mdown and self._collidem():
                self._mdown = False
                self.dispatch.fire("click")
                return True

    def handle_mousehold(self, button, name):
        if name == "left":
            if self._mdown:
                if self._collidem():
                    self.dispatch.fire("mouseholdhover")
                else:
                    self.dispatch.fire("mouseholdoff")
                return True

    def can_handle_key(self, key, string):
        return False

    def handle_keydown(self, key, string):
        if self.can_handle_key(key, string):
            if self.key_active:
                self.dispatch.fire("keypress", key, string)
                return True

    def handle_keyhold(self, key, string):
        if self.can_handle_key(key, string):
            if self.key_active:
                if key in self.key_hold_lengths:
                    if time.time() - self.key_hold_lengths[key] >= self.khl:
                        self.handle_keydown(key, string)
                        self.key_hold_lengths[key] = time.time()
                else:
                    self.key_hold_lenths[key] = time.time()
                return True

    def handle_keyup(self, key, string):
        if self.can_handle_key(key, string):
            if self.key_active:
                if key in self.key_hold_lengths:
                    del self.key_hold_lengths[key]
                return True

    def force_pos_update(self, pos):
        self.pos = pos

    def render(self, offset=(0,0)):
        if self.image:
            x, y = self.pos
            x += offset[0]
            y += offset[1]
            self.image.pos = (x, y)
            self.image.render()
            self.image.pos = self.pos #need to reset!
