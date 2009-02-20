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

    def newline(self):
        """Force the next widget to be on a new line (if pos is not explicitly set) - unless it is already there..."""
        nh = self.next_pos[2]
        self.next_pos = (0, nh+1, nh)


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
           pos must be None or the 2d (x,y) position of the button
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

class Checkbox(Widget):
    """Basic checkbox selection widget."""
    def __init__(self, app, pos=None):
        """Create the Checkbox.
           app must be the App object that this widget is a part of
           pos must be None or the 2d (x,y) position of the button
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets"""
        Widget.__init__(self, app)

        self.off = self.app.regfont.make_text_image("O")
        self.on = self.app.regfont.make_text_image("X")

        if pos == None:
            self.off.pos = self.app.get_next_position(self.off.get_size())
            self.app.set_next_position(self.off.pos, self.off.get_size())
            self.on.pos = self.off.pos
        else:
            self.off.pos = pos
            self.on.pos = pos

        self.state = 0
        self.clicked = False

    def handle_mousedown(self, button, name):
        """Handle a mouse press event from the App."""
        if name == "left":
            if self.off.get_rect().collidepoint(self.app.event_handler.mouse.get_pos()):
                self.clicked = True
                return True
    def handle_mouseup(self, button, name):
        """Handle a mouse release event from the App."""
        if name == "left":
            if self.clicked and self.off.get_rect().collidepoint(self.app.event_handler.mouse.get_pos()):
                self.clicked = False
                self.state = not self.state
                if self.state:
                    self.dispatch.fire("check", self)
                else:
                    self.dispatch.fire("uncheck", self)
                return True
            self.clicked = False

    def render(self):
        """Render the checkbox."""
        self.off.render()
        if self.state:
            self.on.render()

class Radio(Widget):
    """Basic Radio widget."""
    def __init__(self, app, options=[], pos=None):
        """Create the Radio.
           app must be the App object that this widget is a part of
           options must be a list of strings for each option this radio can have
           pos must be None or the 2d (x,y) position of the button
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets"""
        Widget.__init__(self, app)

        self.option = 0
        self.checks = []
        self.labels = []
        height = 0
        width = 0
        for i in options:
            x = Checkbox(app, (0,height))
            x.dispatch.bind("check", self.handle_check)
            self.checks.append(x)
            n = Label(app, i, (int(x.off.get_width()*1.25), height))
            self.labels.append(n)
            height += max([x.off.get_height(), n.text_image.get_height()])
            w = x.off.get_width() + n.text_image.get_width() + 1
            if w > width:
                width = w

        if pos == None:
            x, y = self.app.get_next_position((width, height))
            self.app.set_next_position((x,y), (width, height))
        else:
            x, y = pos
        for i in self.checks:
            a, b = i.off.pos
            a += x
            b += y
            i.off.pos = (a, b)
            i.on.pos = (a, b)
        for i in self.labels:
            a, b = i.text_image.pos
            a += x
            b += y
            i.text_image.pos = (a, b)

    def handle_mousedown(self, button, name):
        """Handle a mouse press event from the App."""
        for i in self.checks:
            x = i.handle_mousedown(button, name)
            if x:
                return True
    def handle_mouseup(self, button, name):
        """Handle a mouse release event from the App."""
        for i in self.checks:
            x = i.handle_mouseup(button, name)
            if x:
                return True
    def handle_check(self, check):
        """Handle a check click from one of the options."""
        for i in self.checks:
            if not i is check:
                i.state = 0
        self.option = self.checks.index(check)

    def render(self):
        """Render the radio."""
        for i in self.checks + self.labels:
            i.render()

class MultiChoiceRadio(Radio):
    """Basic Multiple choice radio widget."""
    def __init__(self, app, options=[], pos=None):
        """Create the MultiChoiceRadio.
           app must be the App object that this widget is a part of
           options must be a list of strings for each option this radio can have
           pos must be None or the 2d (x,y) position of the button
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets"""
        Radio.__init__(self, app, options, pos)

        self.states = []
        for i in self.checks:
            self.states.append(False)
            i.dispatch.bind("uncheck", self.handle_uncheck)

    def handle_check(self, check):
        """Handle a check click from one of the options."""
        self.states[self.checks.index(check)] = True

    def handle_uncheck(self, check):
        """Handle a check unclick from one of the options."""
        self.states[self.checks.index(check)] = False

class Input(Label):
    """Basic text input widget."""
    def __init__(self, app, start_text="", width=100, pos=None):
        """Create the Input widget.
           app must be the App object that this widget is a part of
           start_text must be the string of text the input box starts with
           width must be the max width (in pixels) if the box
           pos must be None or the 2d (x,y) position of the button
               if None, the gui will automaticall assign a position that it tries to fit on screen
               without overlapping other widgets"""
        Label.__init__(self, app, start_text, pos)

        self.width = width
        self.height = self.app.mefont.pygame_font.get_height()

        self.pos = self.text_image.pos
        if pos == None:
            self.app.set_next_position(self.pos, (self.width, self.height))

        self.working = len(self.text)
        print self.app.regfont.pygame_font.size("|")[0]
        self.working_image = image.Animation([[image.create_empty_image((
            int(self.app.mefont.glyphs["|"].get_width()/2),
            self.height)), .5],
                                              [image.create_empty_image((1, 1),(0,0,0,0)), .5]])
        self.xwidth = self.width - self.working_image.get_width()

    def get_clip(self):
        """Return the "clip" of view - to limit rendering outside of the box."""
        rx = 1.0 * view.screen.screen_size[0] / view.screen.screen_size_2d[0]
        ry = 1.0 * view.screen.screen_size[1] / view.screen.screen_size_2d[1]

        x, y = self.pos
        w = self.width
        h = self.height

        return int(x*rx), view.screen.screen_size[1]-int(y*ry)-int(h*ry), int(w*rx), int(h*ry)

    def calc_working_pos(self):
        """Calculate the position of the text cursor - ie, where in the text are we typing..."""
        width = 0
        for i in self.text_image.glyphs[0][0][0:self.working]:
            width += i.get_width()
        x, y = width, self.pos[1]
        if self.text_image.get_width() > self.xwidth:
            x = self.pos[0] - (self.text_image.get_width() - self.xwidth)+x
        return x, y

    def handle_keydown(self, key, string):
        """Handle a key click event from the App."""
        if string in self.app.mefont.acceptable:
            self.text = self.text[0:self.working] + string + self.text[self.working::]
            self.text_image.text = self.text
            self.working += 1
            return True
    def handle_keyhold(self, key, string):
        """Handle a key hold event from the App."""
        pass

    def render(self):
        """Render the Input widget."""
        if self.text_image.get_width() > self.xwidth:
            x, y = self.text_image.pos
            x = self.pos[0] - (self.text_image.get_width() - self.xwidth)
            self.text_image.pos = (x, y)
        else:
            self.text_image.pos = self.pos
        view.screen.push_clip(self.get_clip())
        Label.render(self)
        view.screen.pop_clip()
        self.working_image.pos = self.calc_working_pos()
        self.working_image.render()
