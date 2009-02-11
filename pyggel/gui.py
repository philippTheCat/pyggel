from include import *
import image, event


class App(object):
    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.event_handler.bind_to_event("mouseleft", self.handle_click)
        self.event_handler.bind_to_event("uncaught_event", self.handle_irregular_event)
        self.event_handler.bind_to_event("key", self.handle_key)

        self.widgets = []

    def handle_click(self, *args, **kwargs):
        for i in self.widgets:
            if i.handle_click(*args, **kwargs):
                return

    def handle_irregular_event(self, event, *args, **kwargs):
        if event.type == MOUSEMOTION:
            if self.event_handler.mouse.strings["left"]:
                self.handle_drag(event)
        else:
            for i in self.widgets:
                if i.handle_irregular_event(event, *args, **kwargs):
                    return

    def handle_drag(self, event):
        for i in self.widgets:
            if i.handle_drag(*args, **kwargs):
                return

    def handle_key(self, string, code, *args, **kwargs):
        for i in self.widgets:
            if i.handle_key(string, code, *args, **kwargs):
                return

    def next_widget(self):
        self.widgets.append(self.widgets.pop(0))

    def set_top_widget(self, widg):
        if widg in self.widgets:
            self.widgets.remove(widg)
        self.widgets.insert(0, widg)

    def render(self):
        self.widgets.reverse()
        for i in self.widgets:
            i.render()
        self.widgets.reverse()


class Widget(object):
    def __init__(self, event_handler):
        self.dispatch = event.Dispatcher

        self.event_handler = event_handler

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
