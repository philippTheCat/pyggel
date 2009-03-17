"""
pyggle.gui
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The gui module contains classes to create and use a simple Graphical User Interface.
"""

from include import *
import view, font, event
import time
import image as _image

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
                i.pos = (nw, nh)
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

    def pack_None(self):
        nw = 0
        nh = 0
        newh = 0

        for i in self.app.widgets:
            if isinstance(i, NewLine):
                nw = 0
                nh += newh + i.size[1]
                newh = 0
                i.pos = (nw, nh)
                continue
            if i.override_pos:
                continue
            w, h = i.size
            pos = (nw, nh)
            nw += w
            if h > newh:
                newh = h
            i.force_pos_update(pos)

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

        self.pos = (0,0)
        self.size = view.screen.screen_size_2d

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
            if i.visible:
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
        for i in self.widgets:
            if i.visible:
                if not i == widg:
                    i.unfocus()

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

        self.font = self.app.regfont

        self.dispatch = event.Dispatcher()

        self.visible = True
        self.app.new_widget(self)
        self.image = None
        self.background = None #background image!
        self.tsize = (0,0)
        self.tshift = (0,0)

        self._mhold = False
        self._mhover = False
        self.key_active = False
        self.key_hold_lengths = {}
        self.khl = 150 #milliseconds to hold keys for repeat!

    def get_root_app(self):
        app = self.app
        while hasattr(app, "app") and app.app:
            app = app.app
        return app

    def load_background(self, filename):
        x, y = pygame.image.load(filename).get_size()
        x = int(x/3)
        y = int(y/3)
        new, tsize = _image.load_and_tile_resize_image(filename, (self.size[0]+x*2, self.size[1]+y*2))


        x = new.get_width()/2 - self.size[0]/2
        y = new.get_height()/2 - self.size[1]/2
        tshift = (x, y)
        size = new.get_size()

        return new, size, tsize, tshift

    def pack(self):
        self.app.packer.pack()

    def _collidem(self):
        x, y = self.app.get_mouse_pos()
        a, b = self.pos
        w, h = self.size
        return (x >= a and x <= a+w) and (y >= b and y <= b+h)

    def focus(self):
        self.app.set_top_widget(self)
        self.key_active = True
        self.dispatch.fire("focus")

    def handle_mousedown(self, button, name):
        if name == "left":
            if self._mhover:
                self._mhold = True
                self.focus()
                return True
            self.unfocus()

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
                    if time.time() - self.key_hold_lengths[key] >= self.khl*0.001:
                        self.handle_keydown(key, string)
                        self.key_hold_lengths[key] = time.time()
                else:
                    self.key_hold_lengths[key] = time.time()
                return True

    def handle_keyup(self, key, string):
        if self.can_handle_key(key, string):
            if self.key_active:
                if key in self.key_hold_lengths:
                    del self.key_hold_lengths[key]
                return True

    def handle_uncaught_event(self, event):
        pass

    def get_clip(self):
        x, y = self.pos
        w, h = self.size
        x += self.tsize[0]
        y += self.tsize[1]
        w -= self.tsize[0]*2
        h -= self.tsize[1]*2
        return (x, y), (w, h)

    def force_pos_update(self, pos):
        self.pos = pos

    def render(self, offset=(0,0)):
        x, y = self.pos
        x += offset[0]
        y += offset[1]
        if self.background:
            self.background.pos = (x, y)
            self.background.render()
            self.background.pos = self.pos
        if self.image:
            self.image.pos = (x+self.tshift[0], y+self.tshift[1])
            self.image.render()
            self.image.pos = (self.pos[0]+self.tshift[0], self.pos[1]+self.tshift[1]) #need to reset!

    def unfocus(self):
        self.key_active=False
        self.key_hold_lengths = {}
        self.dispatch.fire("unfocus")

class Frame(App, Widget):
    def __init__(self, app, pos=None, size=(10,10), image=None):
        Widget.__init__(self, app, pos)
        self.size = size

        self.widgets = []

        self.mefont = self.app.mefont
        self.regfont = self.app.regfont

        if image:
            self.background, self.size, self.tsize, self.tshift = self.load_background(image)
        self.packer = Packer(self, size=self.size)
        self.pack()

    def _collidem_c(self):
        x, y = self.app.get_mouse_pos()
        a, b = self.pos
        w, h = self.size
        c, d = self.tshift
        f, g = self.tsize
        return (a+c <= x <= a+w-f) and (b+d <= y <= b+h-g)

    def get_mouse_pos(self):
        x, y = self.app.get_mouse_pos()
        x -= self.pos[0] + self.tshift[0]
        y -= self.pos[1] + self.tshift[1]
        return x, y

    def handle_mousedown(self, button, name):
        Widget.handle_mousedown(self, button, name)
        if self._mhover:
            App.handle_mousedown(self, button, name)
        return self._collidem()

    def handle_mouseup(self, button, name):
        if self._mhold:
            Widget.handle_mouseup(self, button, name)
            App.handle_mouseup(self, button, name)
            return True

    def handle_mousehold(self, button, name):
        Widget.handle_mousehold(self, button, name)
        if self._mhold:
            App.handle_mousehold(self, button, name)
            return True

    def handle_mousemotion(self, change):
        Widget.handle_mousemotion(self, change)
        if self._collidem_c():
            App.handle_mousemotion(self, change)
            return True
        for i in self.widgets:
            i._mhover = False
        return self._collidem()

    def render(self, offset=(0,0)):
        Widget.render(self, offset)
        view.screen.push_clip2d(*self.get_clip())
        self.widgets.reverse()

        x, y = self.pos
        x += offset[0]
        y += offset[1]
        offset = (x+self.tshift[0], y+self.tshift[1])
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
    def __init__(self, app, start_text="", pos=None, image=None, font_color=(1,1,1,1)):
        Widget.__init__(self, app, pos)

        self.text = start_text
        self.image = self.font.make_text_image(self.text, font_color)
        self.image.compile()
        self.size = self.image.get_size()
        if image:
            self.background, self.size, self.tsize, self.tshift = self.load_background(image)
        self.pack()

class Button(Widget):
    def __init__(self, app, text, pos=None, callbacks=[],
                 images=[None, None, None], font_colors=[(1,1,1,1), (1,0,0,1), (0,1,0,1)]):
        Widget.__init__(self, app, pos)
        self.text = text
        self.ireg = self.font.make_text_image(self.text, font_colors[0])
        self.ihov = self.font.make_text_image(self.text, font_colors[1])
        self.icli = self.font.make_text_image(self.text, font_colors[2])
        self.ireg.compile()
        self.ihov.compile()
        self.icli.compile()
        self.image = self.ireg
        self.size = self.image.get_size()

        for i in callbacks:
            self.dispatch.bind("click", i)

        breg, bhov, bcli = images
        if breg:
            self.breg, size, tsize, tshift = self.load_background(breg)
        else:
            self.breg, size, tsize, tshift = None, self.size, self.tsize, self.tshift
        if bhov:
            self.bhov, a, b, c = self.load_background(bhov)
        else:
            self.bhov = None
        if bcli:
            self.bcli, a, b, c = self.load_background(bcli)
        else:
            self.bcli = None
        self.size, self.tsize, self.tshift = size, tsize, tshift
        self.background = self.breg

        self.pack()

        self.handle_mousemotion((0,0)) #make sure we are set to hover at start if necessary!

    def render(self, offset=(0,0)):
        if self._mhover:
            if self._mhold:
                self.image = self.icli
                self.background = self.bcli
            else:
                self.image = self.ihov
                self.background = self.bhov
        else:
            self.image = self.ireg
            self.background = self.breg
        Widget.render(self, offset)

class Checkbox(Widget):
    def __init__(self, app, pos=None, images=[None, None]):
        Widget.__init__(self, app, pos)

        off, on = images

        if off:
            self.off = _image.Image(off)
        else:
            self.off = self.app.regfont.make_text_image("( )")
            self.off.compile()
        if on:
            self.on = _image.Image(on)
        else:
            self.on = self.app.regfont.make_text_image("(!)")
            self.on.compile()
        self.image = self.off

        self.state = 0

        self.size = self.off.get_size()

        self.dispatch.bind("click", self._change_state)
        self.pack()

    def _change_state(self):
        self.state = abs(self.state-1)

    def render(self, offset):
        if self.state:
            self.image = self.on
        else:
            self.image = self.off
        Widget.render(self, offset)

class Radio(Frame):
    def __init__(self, app, pos=None, options=[], images=[None,None,None], font_color=(1,1,1,1)):
        Frame.__init__(self, app, pos)
        self.packer.packtype = None

        self.options = []
        self.states = {}
        fc = font_color

        image = images[0]
        check_images = images[1::]

        w = 0
        for i in options:
            c = Checkbox(self, images=check_images)
            if not self.options:
                c.state = 1
            c.dispatch.bind("click", self.check_click)
            l = Label(self, i, font_color=fc)
            NewLine(self)
            self.options.append([i, c, l, c.state])
            self.states[i] = c.state

            _w = l.pos[0]+l.size[0]
            if _w > w:
                w = _w
        h = max((c.pos[1]+c.size[1],
                 l.pos[1]+l.size[1]))

        self.size = (w, h)
        if image:
            self.background, self.size, self.tsize, self.tshift = self.load_background(image)
        self.pack()

    def check_click(self):
        for i in self.options:
            name, check, label, state = i
            if check.state != state: #changed!
                if check.state: #selected!
                    for x in self.options:
                        if not i == x:
                            x[1].state = 0
                            x[3] = 0
                            self.states[x[0]] = 0
                    state = 1
                else:
                    check.state = 1
            i[0], i[1], i[2], i[3] = name, check, label, state
            self.states[name] = state

class MultiChoiceRadio(Radio):
    def __init__(self, app, pos=None, options=[], images=[None,None,None], font_color=(1,1,1,1)):
        Radio.__init__(self, app, pos, options, images, font_color)

    def check_click(self):
        for i in self.options:
            name, check, label, state = i
            state = check.state
            i[0], i[1], i[2], i[3] = name, check, label, state
            self.states[name] = state

class Input(Widget):
    def __init__(self, app, start_text="", width=100, pos=None, image=None,
                 font_colors=[(1,1,1,1), (.5,.5,.5,1)]):
        Widget.__init__(self, app, pos)

        self.text = start_text
        self.image = self.app.mefont.make_text_image(self.text)

        self.font_colors = font_colors

        self.size = (width, self.app.mefont.pygame_font.get_height())

        self.cursor_pos = len(self.text)
        self.cursor_image = _image.Animation(((self.font.make_text_image("|",color=font_colors[0]), .5),
                                              (self.font.make_text_image("|",color=font_colors[1]), .5)))
        for i in self.cursor_image.frames:
            i[0].compile()
        self.cwidth = int(self.cursor_image.get_width()/2)
        self.xwidth = self.size[0] - self.cwidth*2
        if image:
            self.background, self.size, self.tsize, self.tshift = self.load_background(image)
        self.pack()

        self.calc_working_pos()

    def force_pos_update(self, pos):
        Widget.force_pos_update(self, pos)
        self.calc_working_pos()

    def can_handle_key(self, key, string):
        if string and string in self.app.mefont.acceptable:
            return True
        if key in (K_LEFT, K_RIGHT, K_END, K_HOME, K_DELETE,
                   K_BACKSPACE, K_RETURN):
            return True
        return False

    def submit_text(self):
        if self.text:
            self.dispatch.fire("submit", self.text)
        self.text = ""
        self.image.text = ""
        self.working = 0
        self.calc_working_pos()

    def move_cursor(self, x):
        """Move the cursor position."""
        self.cursor_image.reset()
        self.cursor_pos += x
        if self.cursor_pos < 0:
            self.cursor_pos = 0
        if self.cursor_pos > len(self.text):
            self.cursor_pos = len(self.text)
        self.calc_working_pos()

    def handle_keydown(self, key, string):
        if self.can_handle_key(key, string):
            if self.key_active:
                if key == K_LEFT:
                    self.move_cursor(-1)
                elif key == K_RIGHT:
                    self.move_cursor(1)
                elif key == K_HOME:
                    self.cursor = 0
                elif key == K_END:
                    self.cursor = len(self.text)
                    self.calc_working_pos()
                elif key == K_DELETE:
                    self.text = self.text[0:self.cursor_pos]+self.text[self.cursor_pos+1::]
                    self.image.text = self.text
                    self.calc_working_pos()
                elif key == K_BACKSPACE:
                    if self.cursor_pos:
                        self.text = self.text[0:self.cursor_pos-1]+self.text[self.cursor_pos::]
                        self.move_cursor(-1)
                        self.image.text = self.text
                elif key == K_RETURN:
                    self.submit_text()
                else:
                    self.text = self.text[0:self.cursor_pos] + string + self.text[self.cursor_pos::]
                    self.image.text = self.text
                    self.move_cursor(1)
                return True

    def calc_working_pos(self):
        """Calculate the position of the text cursor - ie, where in the text are we typing... and the text offset."""
        tx, ty = self.pos
        if self.text and self.cursor_pos:
            g1 = self.image.glyphs[0:self.cursor_pos]
            g2 = self.image.glyphs[self.cursor_pos+1::]

            w1 = 0
            w2 = 0
            for i in g1:
                w1 += i.get_width()
            for i in g2:
                w2 += i.get_width()

            tp = tx + self.xwidth - w1 + self.tshift[0]
            if tp > self.pos[0]:
                tp = self.pos[0]

            cp = tp + w1

            self.wpos, self.tpos = (cp+self.cwidth, ty+self.tshift[1]), (tp+self.cwidth*2, ty+self.tshift[1])
        else:
            self.wpos, self.tpos = (tx+self.tshift[0]-self.cwidth, ty+self.tshift[1]), (tx+self.cwidth*2, ty+self.tshift[1])

    def focus(self):
        Widget.focus(self)
        self.cursor_image.reset()

    def render(self, offset=(0,0)):
        """Render the Input widget."""
        tpx, tpy = self.tpos
        tpx += offset[0]
        tpy += offset[1]
        if self.key_active:
            self.image.colorize = self.font_colors[0]
        else:
            self.image.colorize = self.font_colors[1]
        self.image.pos = (tpx, tpy)
        if self.background:
            bx, by = self.pos
            bx += offset[0]
            by += offset[1]
            self.background.pos = (bx, by)
            self.background.render()
            self.background.pos = self.pos
        view.screen.push_clip2d(*self.get_clip())
        self.image.render()
        self.image.pos = self.tpos
        view.screen.pop_clip()
        if self.key_active:
            wpx, wpy = self.wpos
            wpx += offset[0]
            wpy += offset[1]
            self.cursor_image.pos = (wpx, wpy)
            self.cursor_image.render()
            self.cursor_image.pos = self.wpos

class MoveBar(Widget):
    def __init__(self, app, title="", pos=(0,0), width=100, image=None, child=None):
        Widget.__init__(self, app, pos)
        self.override_pos = True #window is always overridden,sorry :P

        self.title = title

        self.child = child
        if self.child:
            self.child.override_pos = True
            self.size = (self.child.size[0]-self.child.tsize[0]*2, self.app.mefont.pygame_font.get_height())
            self.child.pos = (self.pos[0], self.pos[1]+self.size[1])
        else:
            self.size = (width, self.app.mefont.pygame_font.get_height())

        if image:
            self.background, self.size, self.tsize, self.tshift = self.load_background(image)
        if self.child:
            x, y = self.child.pos
            y += self.tsize[1]*2-1
            self.child.pos = (x, y)

        i = self.font.make_text_image(title)
        if i.get_width() > self.size[0] - self.tsize[0]*2:
            while title and self.font.make_text_image(title+"...").get_width() > self.size[0] - self.tsize[0]*2:
                title = title[0:-1]
            i = self.font.make_text_image(title+"...")
        self.image = i
        self.image.compile()
        self.pack()

    def handle_mousemotion(self, change):
        _retval = Widget.handle_mousemotion(self, change)
        if self._mhold:
            x, y = self.pos
            x += change[0]
            y += change[1]
            self.pos = (x, y)
            self._mhover = self._collidem()
            if self.child:
                x, y = self.child.pos
                x += change[0]
                y += change[1]
                self.child.pos = (x, y)
            return True
        return _retval

    def focus(self):
        if self.child:
            self.child.focus()
        Widget.focus(self)

    def unfocus(self):
        if self.child == self.app.widgets[0] and not self == self.app.widgets[1]:
            Widget.focus(self)
        else:
            Widget.unfocus(self)

class Window(MoveBar):
    def __init__(self, app, title="", pos=(0,0), size=(10,10), images=[None, None]):
        child = Frame(app, pos, size, images[1])
        MoveBar.__init__(self, app, title, pos, size[0], images[0], child)

        self.packer = self.child.packer
        self.mefont = self.child.mefont
        self.regfont = self.child.regfont
        self.pack()

    def new_widget(self, widg):
        widg.app = self.child
        self.child.new_widget(widg)

    
class Menu(Button):
    def __init__(self, app, name="", pos=None, options=[], images=[None,None,None,None],
                 font_colors=[(1,1,1,1), (1,0,0,1), (0,1,0,1)], callback=None):
        Button.__init__(self, app, name, pos, [], images[1::], font_colors)
        self.dispatch.bind("click", self.do_visible)

        self.frames = []
        self.cur_frame = 0

        self.add_frame("", options, images, font_colors)

        if callback:
            self.dispatch.bind("menu-click", callback)

    def add_frame(self, name, options, images, fc):
        goback = int(self.cur_frame)
        frame = Frame(self.get_root_app(), (self.pos[0], self.pos[1]+self.size[1]), image=images[0])
        frame.packer.packtype = None
        frame.visible = False
        frame.dispatch.bind("unfocus", self.do_unfocus)
        self.frames.append(frame)

        self.cur_frame = len(self.frames)-1

        bimages = images[1::]

        w = 0
        if not frame == self.frames[0]:
            c = Button(frame, "../", images=bimages, font_colors=fc)
            NewLine(frame)
            w = c.size[0]
            c.dispatch.bind("click", self.swap_frame(goback))

        for i in options:
            if type(i) is type(""):
                c = Button(frame, i, images=bimages, font_colors=fc)
                NewLine(frame)
                if c.size[0] > w:
                    w = c.size[0]
                if name:
                    ni = name+"."+i
                else:
                    ni = i
                c.dispatch.bind("click", self.bind_to_event(ni))
                c.dispatch.bind("click", self.do_unfocus)
            else:
                c = Button(frame, i[0], images=bimages, font_colors=fc)
                NewLine(frame)
                if c.size[0] > w:
                    w = c.size[0]
                c.dispatch.bind("click", self.swap_frame(self.cur_frame+1))
                if name:
                    ni = name+"."+i[0]
                else:
                    ni = i[0]
                self.add_frame(ni, i[1::], images, fc)
        if options:
            h = c.pos[1]+c.size[1]
        else:
            h = 1
        for i in frame.widgets:
            if not isinstance(i, NewLine):
                i.size = w-i.tsize[0]*2, i.size[1]-i.tsize[1]*2
                if i.breg: i.breg, _size, a, i.tshift = i.load_background(bimages[0])
                if i.bhov: i.bhov, c, a, b = i.load_background(bimages[1])
                if i.bcli: i.bcli, c, a, b = i.load_background(bimages[2])
                i.size = _size
        i.pack()

        frame.size = (w, h)
        if images[0]:
            frame.background, frame.size, frame.tsize, frame.tshift = frame.load_background(images[0])

        x, y = frame.pos
        while x + frame.size[0] > frame.app.size[0]:
            x -= 1
        while y + frame.size[1] > frame.app.size[1]:
            y -= 1
        frame.pos = (x, y)
        self.cur_frame = goback

    def do_swap_frame(self, num):
        self.cur_frame = num
        for i in self.frames:
            i.visible = False
        self.frames[num].visible = True
        self.frames[num].focus()

    def swap_frame(self, num):
        def do():
            self.do_swap_frame(num)
        return do

    def do_visible(self):
        self.do_swap_frame(0)

    def bind_to_event(self, name):
        def send():
            self.dispatch.fire("menu-click", name)
        return send

    def do_unfocus(self):
        for i in self.frames:
            i.visible = False
        self.unfocus()

    def unfocus(self):
        if not self.frames[self.cur_frame].visible:
            Widget.unfocus(self)
