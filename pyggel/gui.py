"""
pyggle.gui
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The gui module contains classes to create and use a simple Graphical User Interface.
"""

from include import *
import image, event, view, font


class App(object):
    """A simple Application class, to hold and control all widgets."""
    def __init__(self, event_handler, suppress_events=True):
        """Create the App.
           event_handler must be the event.Handler object that the gui will use to get events,
           and each event handler may only have on App attached to it."""
        self.event_handler = event_handler
        self.event_handler.gui_suppress_events = suppress_events
        self.event_handler.gui = self

        self.widgets = []

        self.dispatch = event.Dispatcher()
        self.dispatch.bind("new-widget", self.new_widget)

        self.next_pos = 0, 0, 0 #left, top, bottom if shift

        self.mefont = font.MEFont()
        self.regfont = font.Font()

        self.visible = True

    def new_widget(self, widget):
        """Add a new widget to the App."""
        if not widget in self.widgets:
            self.widgets.insert(0, widget)

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
            if i.handle_drag(*args, **kwargs):
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
        """Renders all widgets, camera can be None or teh camera object used to render the scene."""
        self.widgets.reverse()
        for i in self.widgets:
            if i.visible: i.render()
        self.widgets.reverse()

    def get_next_position(self, size):
        """Get next 'pad' position, ie, the next open area that this widget can be rendered to without overlapping other widgets."""
        x, y, nh = self.next_pos
        w, h = size
        if x + w > view.screen.screen_size_2d[0]:
            x = 0
            y = nh + 1
        return x, y

    def set_next_position(self, pos, size):
        """Change the next position for the next widget."""
        x, y = pos[0] + size[0] + 1, pos[1]
        if y + size[1] > self.next_pos[2]:
            nh = y + size[1]
        else:
            nh = self.next_pos[2]

        self.next_pos = x, y, nh


class Widget(object):
    """Base class all gui elements should inherit from."""
    def __init__(self, app):
        """Create the Widget.
           app must be the App object that this widget is part of."""
        self.app = app
        self.dispatch = event.Dispatcher()

        self.visible = True

        self.app.dispatch.fire("new-widget", self)

    def handle_mousedown(self, button, name):
        """Handle a mouse down event from the App."""
        return False
    def handle_mouseup(self, button, name):
        """Handle a mouse release event from the App."""
        return False
    def handle_mousehold(self, button, name):
        """Handle a mouse hold event from the App."""
        return False

    def handle_drag(self, event):
        """Handle a mouse drag event from the App."""
        return False

    def handle_uncaught_event(self, event):
        """Handle an uncaught event from the App."""
        return False

    def handle_keydown(self, key, string):
        """Handle a key press event from the App."""
        return False
    def handle_keyup(self, key, string):
        """Handle a key release event from the App."""
        return False
    def handle_keyhold(self, key, string):
        """Handle a key hold event from the App."""
        return False

    def render(self):
        """Render the widget."""
        pass

class Label(Widget):
    """A simple text label widget."""
    def __init__(self, app, text, pos=None):
        """Create the Label.
           app must be the App object that this widget is a part of
           text must be the text string to render (supports smileys, via the app.mefont object)
           pos must be None or the 2d (x,y) position of the label
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets"""
        Widget.__init__(self, app)

        self.text = text
        self.text_image = self.app.mefont.make_text_image(text)

        if pos == None:
            self.text_image.pos = self.app.get_next_position(self.text_image.get_size())
            self.app.set_next_position(self.text_image.pos, self.text_image.get_size())
        else:
            self.text_image.pos = pos

    def render(self):
        """Render the Label."""
        self.text_image.render()

class Button(Label):
    """A simple button widget."""
    def __init__(self, app, text, pos=None, callbacks=[]):
        """Create the Button.
           app must be the App object that this widget is a part of
           text must be the text string to render (supports smileys, via the app.mefont object)
           pos must be None or the 2d (x,y( position of the button
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets
           callbacks must be a list/tuple of functions/methods to call when the button is clicked"""
        Label.__init__(self, app, text, pos)
        self.text_image_click = self.text_image.copy()
        self.text_image_click.colorize=(1,0,0,1)

        self.use_image = self.text_image

        for i in callbacks:
            self.dispatch.bind("click", i)

    def handle_mousedown(self, button, name):
        """Handle a mouse down event from the App."""
        if name == "left":
            if self.use_image.get_rect().collidepoint(self.app.event_handler.mouse.get_pos()):
                self.use_image = self.text_image_click
                return True

    def handle_mousehold(self, button, name):
        """Handle a mouse hold event from the App."""
        if name == "left":
            if self.use_image == self.text_image_click:
                if self.use_image.get_rect().collidepoint(self.app.event_handler.mouse.get_pos()):
                    return True
            self.use_image = self.text_image

    def handle_mouseup(self, button, name):
        """Handle a mouse release (possible click) event from the App.
           If clicked, will execute all callbacks (if any) supplied."""
        if name == "left":
            if self.use_image == self.text_image_click:
                if self.use_image.get_rect().collidepoint(self.app.event_handler.mouse.get_pos()):
                    self.dispatch.fire("click")
                    self.use_image = self.text_image
                    return True

    def render(self):
        """Render the button."""
        self.use_image.render()
