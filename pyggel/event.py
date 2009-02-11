from include import *
import view
import string

class Keyboard(object):
    def __init__(self):
        self.active = []
        self.hook = {}

        self.hit = []
        self.held = []

class Mouse(object):
    all_names = {1:"left", 2:"middle", 3:"right", 4:"wheel-up", 5:"wheel-down"}
    def __init__(self):
        self.active = []

        self.hit = []
        self.held = []

    def get_pos(self):
        rx = 1.0 * view.screen.screen_size_2d[0] / view.screen.screen_size[0]
        ry = 1.0 * view.screen.screen_size_2d[1] / view.screen.screen_size[1]

        mx, my = pygame.mouse.get_pos()

        return int(mx*rx), int(my*ry)

    def get_name(self, button):
        if button in self.all_names:
            return self.all_names[button]
        return "extra-%s"%button

class Dispatcher(object):
    def __init__(self):
        self.name_bindings = {}

    def bind(self, name, function):
        if name in self.name_bindings:
            self.name_bindings[name].append(function)
        else:
            self.name_bindings[name] = [function]

    def fire(self, name, *args, **kwargs):
        if name in self.name_bindings:
            for func in self.name_bindings[name]:
                func(*args, **kwargs)

class Handler(object):
    def __init__(self):
        self.keyboard = Keyboard()
        self.mouse = Mouse()
        self.quit = False

        self.dispatch = Dispatcher()

        self.uncaught_events = []

    def bind_to_event(self, event, function):
        self.dispatch.bind(event, function)

    def update(self):
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
