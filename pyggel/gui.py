from include import *
import image, event, view, font


class App(object):
    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.event_handler.bind_to_event("mousedown", self.handle_click)
        self.event_handler.bind_to_event("uncaught_event", self.handle_irregular_event)
        self.event_handler.bind_to_event("keydown", self.handle_key)

        self.widgets = []

        self.dispatch = event.Dispatcher()
        self.dispatch.bind("new-widget", self.new_widget)

        self.next_pos = 0, 0, 0 #left, top, bottom if shift

        self.mefont = font.MEFont()
        self.regfont = font.Font()

        self.visible = True

    def new_widget(self, widget):
        self.widgets.insert(0, widget)

    def handle_click(self, button, name):
        for i in self.widgets:
            if i.visible:
                if i.handle_click(button, name):
                    return

    def handle_irregular_event(self, event):
        if event.type == MOUSEMOTION:
            if self.event_handler.mouse.strings["left"]:
                self.handle_drag(event)
        else:
            for i in self.widgets:
                if i.visible:
                    if i.handle_irregular_event(event):
                        return

    def handle_drag(self, event):
        for i in self.widgets:
            if i.handle_drag(*args, **kwargs):
                return

    def handle_key(self, key, string):
        for i in self.widgets:
            if i.visible:
                if i.handle_key(key, string):
                    return

    def next_widget(self):
        self.widgets.append(self.widgets.pop(0))
        while not self.widgets[0].visible:
            self.widgets.append(self.widgets.pop(0))

    def set_top_widget(self, widg):
        if widg in self.widgets:
            self.widgets.remove(widg)
        self.widgets.insert(0, widg)

    def render(self):
        self.widgets.reverse()
        for i in self.widgets:
            if i.visible: i.render()
        self.widgets.reverse()

    def get_next_position(self, size):
        x, y, nh = self.next_pos
        w, h = size
        if x + w > view.screen.screen_size_2d[0]:
            x = 0
            y = nh + 1
        return x, y

    def set_next_position(self, pos, size):
        x, y = pos[0] + size[0] + 1, pos[1]
        if y + size[1] > self.next_pos[2]:
            nh = y + size[1]
        else:
            nh = self.next_pos[2]

        self.next_pos = x, y, nh


class Widget(object):
    def __init__(self, app):
        self.app = app
        self.dispatch = event.Dispatcher()

        self.visible = True

        self.app.dispatch.fire("new-widget", self)

    def handle_click(self, button, name):
        return False

    def handle_drag(self, event):
        return False

    def handle_irregular_event(self, event):
        return False

    def handle_key(self, key, string):
        return False

    def render(self):
        pass

class Label(Widget):
    def __init__(self, app, text, pos=None):
        Widget.__init__(self, app)

        self.text = text
        self.text_image = self.app.mefont.make_text_image(text)

        if pos == None:
            self.text_image.pos = self.app.get_next_position(self.text_image.get_size())
            self.app.set_next_position(self.text_image.pos, self.text_image.get_size())
        else:
            self.text_image.pos = pos

    def render(self):
        self.text_image.render()

class Button(Label):
    def __init__(self, app, text, pos=None, callbacks=[]):
        Label.__init__(self, app, text, pos)
        self.text_image_click = self.text_image.copy()
        self.text_image_click.colorize=(1,0,0,1)

        self.use_image = self.text_image

        self.app.event_handler.bind_to_event("mousedown", self.check_click)
        self.app.event_handler.bind_to_event("mousehold", self.check_hold)
        self.app.event_handler.bind_to_event("mouseup", self.check_unclick)

        for i in callbacks:
            self.dispatch.bind("click", i)

    def check_click(self, button, name):
        if name == "left":
            if self.use_image.get_rect().collidepoint(self.app.event_handler.mouse.get_pos()):
                self.use_image = self.text_image_click

    def check_hold(self, button, name):
        if name == "left":
            if self.use_image == self.text_image_click:
                if self.use_image.get_rect().collidepoint(self.app.event_handler.mouse.get_pos()):
                    self.use_image = self.text_image_click
                    return
        self.use_image = self.text_image

    def check_unclick(self, button, name):
        if name == "left":
            if self.use_image == self.text_image_click:
                if self.use_image.get_rect().collidepoint(self.app.event_handler.mouse.get_pos()):
                    self.dispatch.fire("click")
            self.use_image = self.text_image

    def render(self):
        self.use_image.render()