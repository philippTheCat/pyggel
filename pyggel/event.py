"""
pyggle.event
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The event module contains classes to grab and access events.
"""

from include import *
import view
import string

class Keyboard(object):
    """A simple class to store keyboard events."""
    def __init__(self):
        """Create the holder.
           Attributes:
               active -> a list of all keys hit or held
               hit -> a list of all keys hit
               held -> a list of all keys held"""
        self.active = []
        self.hook = {}

        self.hit = []
        self.held = []

class Mouse(object):
    """A simple class to store mouse events."""
    all_names = {1:"left", 2:"middle", 3:"right", 4:"wheel-up", 5:"wheel-down"}
    def __init__(self):
        """Create the holder.
           Attributes:
               active -> a list of all mouse buttons that were clicked or held
               hit -> a list of all mouse buttons that were clicked
               held -> a list of all mouse buttons that were held"""
        self.active = []

        self.hit = []
        self.held = []

    def get_pos(self):
        """Return the mouse pos."""
        return view.screen.get_mouse_pos()

    def get_name(self, button):
        """Return the 'name' that matches the button, ie:
           1 -> left
           2 -> middle
           3 -> right"""
        if button in self.all_names:
            return self.all_names[button]
        return "extra-%s"%button

class Dispatcher(object):
    """A simple dispatcher class, that allows you to bind functions to events, and execute them all with a single command."""
    def __init__(self):
        """Create the Dispatcher object."""
        self.name_bindings = {}

    def bind(self, name, function):
        """Bind 'function' to the event 'name'.
           name can be anything that works as a python dict key (string, number, etc.)
           function must be a python function or method"""
        if name in self.name_bindings:
            self.name_bindings[name].append(function)
        else:
            self.name_bindings[name] = [function]

    def fire(self, name, *args, **kwargs):
        """Execute command 'name', calls any functions bound to this event with args/kwargs.
           name can be anything that works as a python dict key (string, number, etc.)
           *args/**kwargs are the arguments to use on any function calls bound to this event"""
        if name in self.name_bindings:
            for func in self.name_bindings[name]:
                func(*args, **kwargs)

class Handler(object):
    """A simple event handler. This object catches and stores events, as well as fire off any callbacks attached to them.
       There should only ever be one Handler in use at once, as only one handler can get a specific event."""
    def __init__(self):
        """Create the handler.
           Attributes:
               keyboard -> a Keyboard object storing keyboard events
               mouse -> a Mouse object storing mouse events
               quit -> bool - whether wuit signal has been sent
               dispatch -> Dispatcher object used for firing callbacks
               uncaught_events -> list of all events the Handler couldn't handle"""
        self.keyboard = Keyboard()
        self.mouse = Mouse()
        self.quit = False

        self.dispatch = Dispatcher()

        self.uncaught_events = []

    def bind_to_event(self, event, function):
        """Bind a callback function to an event.
           event must be the name of an input event, event names are:
               keydown - when a key is pressed
               keyup - when a key is released
               keyhold - when a mouse key is held
               mousedown - when a mouse button is pressed
               mouseup - when a mouse button is released
               mousehold - when a mouse button is held
               quit - when the QUIT event was fired (ie the X box on the window is hit)
               uncaught-event - when an unsupported event is fired
               update - called at end of grabbing events/firing callbacks.
           function must be a python function or method that accepts the proper args for each event,
           event args are:
               keydown, keyup, keyhold: key->Pygame event key, string->the "string" of the key
                   string will be the key pressed, ie, the a key is "a" (or "A" with shift/caps)
               mousedown, mouseup, mousehold: button->Pygame event button, string-> the "name" of the button
                   string will be "left", "right", "middle", "wheel-up", "wheel-down", or "extra-N" where N is the Pygame event button
               uncaught-event: event->the Pygame event
               quit, update: None"""
        self.dispatch.bind(event, function)

    def update(self):
        """Grab all events, store in proper objects, and fire callbacks where necessary."""
        self.keyboard.hit = []
        self.mouse.hit = []
        self.uncaught_events = []
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if not event.key in self.keyboard.active:
                    self.keyboard.active.append(event.key)
                    self.keyboard.active.append(str(event.unicode))
                    self.keyboard.hit.append(event.key)
                    self.keyboard.hit.append(str(event.unicode))
                    self.keyboard.hook[event.key] = str(event.unicode)

                self.dispatch.fire("keydown", event.key, str(event.unicode))

            elif event.type == KEYUP:
                if event.key in self.keyboard.active:
                    self.keyboard.active.remove(event.key)
                    self.keyboard.active.remove(self.keyboard.hook[event.key])
                    self.dispatch.fire("keyup", event.key, self.keyboard.hook[event.key])
                    del self.keyboard.hook[event.key]
                else:
                    self.dispatch.fire("uncaught-event", event)

            elif event.type == MOUSEBUTTONDOWN:
                name = self.mouse.get_name(event.button)
                if not event.button in self.mouse.active:
                    self.mouse.active.append(event.button)
                    self.mouse.active.append(name)
                    self.mouse.hit.append(event.button)
                    self.mouse.hit.append(name)
                self.dispatch.fire("mousedown", event.button, name)

            elif event.type == MOUSEBUTTONUP:
                name = self.mouse.get_name(event.button)
                if event.button in self.mouse.active:
                    self.mouse.active.remove(event.button)
                    self.mouse.active.remove(name)
                self.dispatch.fire("mouseup", event.button, name)
                
            elif event.type == QUIT:
                self.quit = True
                self.dispatch.fire("quit")

            else:
                self.uncaught_events.append(event)
                self.dispatch.fire("uncaught-event", event)

        for i in self.keyboard.active:
            if not i in self.keyboard.hit:
                if i in self.keyboard.hook: #make sure these aren't the string names! Or else we would double fire, potentially
                    eventkey = i
                    name = self.keyboard.hook[eventkey]
                    self.dispatch.fire("keyhold", eventkey, name)
                if not i in self.keyboard.held:
                    self.keyboard.held.append(i) #regardless of type now!
        for i in self.mouse.active:
            if not i in self.mouse.hit:
                if type(i) is type(1): #same thing as keys, only slightly different test!
                    self.dispatch.fire("mousehold", i, self.mouse.get_name(i))
                if not i in self.mouse.held:
                    self.mouse.held.append(i)
        self.dispatch.fire("update")
