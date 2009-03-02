"""
pyggle.gui
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The gui module contains classes to create and use a simple Graphical User Interface.
"""

from include import *
import image, view, font, event
import time

class Packer(object):
    def __init__(self, app=None, packtype="wrap", size=(10,10)):
        self.app = app
        self.packtype = packtype
        self.size = size

        self.need_to_pack = False

    def pack(self):
        self.app.widgets.reverse()
        getattr(self, "pack_%s"%self.packtype)()
        self.app.widgets.reverse()
        self.need_to_pack = False

    def pack_wrap(self):
        nw = 0
        nh = 0
        newh = 0

        for i in self.app.widgets:
            if isinstance(i, NewLine):
                nw = 0
                nh += newh + i.size[1]
                newh = 0
                continue
            if i.override_pos:
                continue
            w, h = i.size
            if nw + w > self.size[0] and nw:
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

    def pack_center(self):
        rows = [[]]
        w = 0
        for i in self.app.widgets:
            if isinstance(i, NewLine):
                rows.append([i])
                rows.append([])
                continue
            if i.override_pos:
                continue
            rows[-1].append(i)
            w += i.size[0]
            if w >= self.size[0]:
                rows.append([])
                w = 0

        sizes = []
        for row in rows:
            h = 0
            w = 0
            for widg in row:
                if widg.size[1] > h:
                    h = widg.size[1]
                w += widg.size[0]
            sizes.append((w, h))

        center = self.size[1] / 2
        height = 0
        for i in sizes:
            height += i[1]
        top = center - height / 2
        for i in xrange(len(rows)):
            w = self.size[0] / 2 - sizes[i][0] / 2
            for widg in rows[i]:
                widg.force_pos_update((w, top))
                w += widg.size[0]
            top += sizes[i][1]

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

        self.mefont = font.MEFont()
        self.regfont = font.Font()

        self.packer = Packer(self, size=view.screen.screen_size)

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

    def handle_mousemotion(self, change):
        """Callback for mouse motion events from event_handler."""
        for i in self.widgets:
            if i.handle_mousemotion(change):
                return True

    def handle_uncaught_event(self, event):
        """Callback for uncaught_event events from event_handler."""
        for i in self.widgets:
            if i.visible:
                if i.handle_uncaught_event(event):
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
        self.app.new_widget(self)
        self.image = None

        self._mhold = False
        self._mhover = False
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
            if self._mhover:
                self._mhold = True
                return True

    def handle_mouseup(self, button, name):
        if name == "left":
            if self._mhold and self._mhover:
                self._mhold = False
                self.dispatch.fire("click")
                return True

    def handle_mousehold(self, button, name):
        if name == "left":
            if self._mhold:
                return True

    def handle_mousemotion(self, change):
        self._mhover = self._collidem()
        for i in self.app.widgets:
            if not i == self:
                i._mhover = False
        return self._mhover

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

    def handle_uncaught_event(self, event):
        pass

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

class Frame(App, Widget):
    def __init__(self, app, pos=None, size=(10,10)):
        Widget.__init__(self, app, pos)
        self.size = size

        self.widgets = []

        self.mefont = self.app.mefont
        self.regfont = self.app.regfont

        self.packer = Packer(self, size=self.size)
        self.pack()

    def render(self, offset=(0,0)):
        view.screen.push_clip2d(self.pos, self.size)
        self.widgets.reverse()

        x, y = self.pos
        x += offset[0]
        y += offset[1]
        offset = (x, y)
        for i in self.widgets:
            if i.visible: i.render(offset)
        self.widgets.reverse()
        view.screen.pop_clip()

class NewLine(Widget):
    def __init__(self, app, height=0):
        Widget.__init__(self, app)
        self.size = (0, height)
        self.pack()

class Label(Widget):
    def __init__(self, app, start_text="", pos=None):
        Widget.__init__(self, app, pos)

        self.text = start_text
        self.image = self.app.mefont.make_text_image(self.text)
        self.size = self.image.get_size()
        self.pack()

class Button(Widget):
    def __init__(self, app, text, pos=None, callbacks=[]):
        Widget.__init__(self, app, pos)
        self.text = text
        self.ireg = self.app.mefont.make_text_image(self.text)
        self.ihov = self.app.mefont.make_text_image(self.text, (1, 0, 0, 1))
        self.icli = self.app.mefont.make_text_image(self.text, (0, 1, 0, 1))
        self.image = self.ireg
        self.size = self.image.get_size()

        for i in callbacks:
            self.dispatch.bind("click", i)

        self.pack()

        self.handle_mousemotion((0,0)) #make sure we are set to hover at start if necessary!

    def render(self, offset=(0,0)):
        if self._mhover:
            if self._mhold:
                self.image = self.icli
            else:
                self.image = self.ihov
        else:
            self.image = self.ireg
        Widget.render(self, offset)
