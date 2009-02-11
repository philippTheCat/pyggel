from include import *
import image, event, view, font


class App(object):
    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.event_handler.bind_to_event("mouseleft", self.handle_click)
        self.event_handler.bind_to_event("uncaught_event", self.handle_irregular_event)
        self.event_handler.bind_to_event("key", self.handle_key)

        self.widgets = []

        self.dispatch = event.Dispatcher()
        self.dispatch.bind("new-widget", self.new_widget)

        self.next_pos = [0,0]

        self.mefont = font.MEFont()
        self.regfont = font.Font()

        self.visible = True

    def new_widget(self, widget):
        self.widgets.insert(0, widget)

    def handle_click(self, *args, **kwargs):
        for i in self.widgets:
            if i.visible:
                if i.handle_click(*args, **kwargs):
                    return

    def handle_irregular_event(self, event, *args, **kwargs):
        if event.type == MOUSEMOTION:
            if self.event_handler.mouse.strings["left"]:
                self.handle_drag(event)
        else:
            for i in self.widgets:
                if i.visible:
                    if i.handle_irregular_event(event, *args, **kwargs):
                        return

    def handle_drag(self, event):
        for i in self.widgets:
            if i.handle_drag(*args, **kwargs):
                return

    def handle_key(self, string, code, *args, **kwargs):
        for i in self.widgets:
            if i.visible:
                if i.handle_key(string, code, *args, **kwargs):
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
        x, y = self.next_pos
        w, h = size
        if x + w > view.screen.screen_size_2d[0]:
            x = 0
            y += h + 1
        return x, y

    def set_next_position(self, pos, size):
        self.next_pos = pos[0] + size[0] + 1, pos[1]


class Widget(object):
    def __init__(self, app):
        self.app = app
        self.dispatch = event.Dispatcher()

        self.visible = True

        self.app.dispatch.fire("new-widget", self)

    def handle_click(self, *args, **kwargs):
        return False

    def handle_drag(self, *args, **kwargs):
        return False

    def handle_irregular_event(self, event, *args, **kwargs):
        return False

    def handle_key(self, string, code, *args, **kwargs):
        return False

    def render(self):
        pass

class Label(Widget):
    def __init__(self, app, text, pos=None):
        Widget.__init__(self, app)

        self.text = text
        self.text_image = self.app.regfont.make_text_image(text)

        if pos == None:
            self.text_image.pos = self.app.get_next_position(self.text_image.get_size())
            self.app.set_next_position(self.text_image.pos, self.text_image.get_size())
        else:
            self.text_image.pos = pos

    def render(self):
        self.text_image.render()
