from include import *
import view
import string

class Keyboard(object):
    def __init__(self):
        self.strings = {}
        for s in string.printable[0:-5]:
            self.strings[s] = False
        self.scancodes = {}

        self.active = []
        self.all = []

        self.hit = []

class Mouse(object):
    def __init__(self):
        self.strings = {}
        for s in ["left", "right", "middle", "wheel-up", "wheel-down"]:
            self.strings[s] = False

        self.extra = {}

        self.active = []
        self.all = []

        self.hit = []

    def get_pos(self):
        rx = 1.0 * view.screen.screen_size_2d[0] / view.screen.screen_size[0]
        ry = 1.0 * view.screen.screen_size_2d[1] / view.screen.screen_size[1]

        mx, my = pygame.mouse.get_pos()

        return int(mx*rx), int(my*ry)

class Handler(object):
    def __init__(self):
        self.keyboard = Keyboard()
        self.mouse = Mouse()
        self.quit = False

        self.name_bindings = {}

    def bind_to_event(self, event, function, args=[]):
        if event in self.name_bindings:
            self.name_bindings[event].append([function, args])
        else:
            self.name_bindings[event] = [[function, args]]

    def update(self):
        self.keyboard.hit = []
        self.mouse.hit = []
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                s = str(event.unicode)
                self.keyboard.scancodes[event.scancode] = s
                if s in self.keyboard.strings:
                    self.keyboard.strings[s] = True
                    if s in self.name_bindings:
                        for func in self.name_bindings[s]:
                            func[0](*func[1])
                if not event.key in self.keyboard.active:
                    self.keyboard.active.append(event.key)

                if event.key in self.name_bindings:
                    for func in self.name_bindings[event.key]:
                        func[0](*func[1])

                self.keyboard.hit.extend([s, event.key])

            if event.type == KEYUP:
                s = self.keyboard.scancodes[event.scancode]
                if s in self.keyboard.strings:
                    self.keyboard.strings[s] = False
                if event.key in self.keyboard.active:
                    self.keyboard.active.remove(event.key)

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mouse.hit.append("left")
                    self.mouse.strings["left"] = True
                    if "mouseleft" in self.name_bindings:
                        for func in self.name_bindings["mouseleft"]:
                            func[0](*func[1])
                elif event.button == 2:
                    self.mouse.hit.append("middle")
                    self.mouse.strings["middle"] = True
                    if "mousemiddle" in self.name_bindings:
                        for func in self.name_bindings["mousemiddle"]:
                            func[0](*func[1])
                elif event.button == 3:
                    self.mouse.hit.append("right")
                    self.mouse.strings["right"] = True
                    if "mouseright" in self.name_bindings:
                        for func in self.name_bindings["mouseright"]:
                            func[0](*func[1])
                elif event.button == 4:
                    self.mouse.hit.append("wheel-up")
                    self.mouse.strings["wheel-up"] = True
                    if "mousewheel-up" in self.name_bindings:
                        for func in self.name_bindings["mousewheel-up"]:
                            func[0](*func[1])
                elif event.button == 5:
                    self.mouse.hit.append("wheel-down")
                    self.mouse.strings["wheel-down"] = True
                    if "mousewheel-down" in self.name_bindings:
                        for func in self.name_bindings["mousewheel-down"]:
                            func[0](*func[1])
                else:
                    self.mouse.hit.append("mouse-extra%s"%event.button)
                    self.mouse.extra[event.button] = True
                    if "mouse-extra%s"%event.button in self.name_bindings:
                        for func in self.name_bindings["mouse-extra%s"%event.button]:
                            func[0](*func[1])

                if not event.button in self.mouse.active:
                    self.mouse.active.append(event.button)

                self.mouse.hit.append(event.button)

            if event.type == MOUSEBUTTONUP:
                if event.button == 1: self.mouse.strings["left"] = False
                elif event.button == 2: self.mouse.strings["middle"] = False
                elif event.button == 3: self.mouse.strings["right"] = False
                elif event.button == 4: self.mouse.strings["wheel-up"] = False
                elif event.button == 5: self.mouse.strings["wheel-down"] = False
                else: self.mouse.extra[event.button] = False
                if event.button in self.mouse.active:
                    self.mouse.active.remove(event.button)
                
            if event.type == QUIT:
                self.quit = True
                if "quit" in self.name_bindings:
                    for func in self.name_bindings["quit"]:
                        func[0](*func[1])
        self.keyboard.all = pygame.key.get_pressed()
        self.mouse.all = pygame.mouse.get_pressed()
