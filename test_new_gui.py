import pyggel
from pyggel import *

import random

def test_callback():
    print "woo!"
def test_menu(item):
    print item
def swap_apps(new):
    new.activate()

def main():
    pyggel.init()

    scene = pyggel.scene.Scene()

    eh = pyggel.event.Handler()
    app = pyggel.Newgui.App(eh)
    app.theme.load("data/gui/theme.py")
    newapp = pyggel.Newgui.App(eh)
    newapp.theme = app.theme
    app.activate() #first one ;)
    regfont = app.get_regfont("default")
    mefont = app.get_mefont("default")
    regfont.add_image(":P", pyggel.image.GridSpriteSheet("data/ar.png", (3,3)))
    mefont.add_image(":P", pyggel.image.GridSpriteSheet("data/ar.png", (3,3)))
    app.packer.packtype="center"
    scene.add_2d(app)
    scene.add_2d(newapp)

    frame = pyggel.Newgui.Frame(app, (500, 0), (140, 300), background_image="data/gui/base.png")
    frame.packer.packtype = "wrap"

    pyggel.Newgui.Button(frame, "click!:P", callbacks=[test_callback],
                         background_image="data/gui/base.png",
                         background_image_hover="data/gui/base.png",
                         font_underline=True)
    pyggel.Newgui.Button(frame, "click!124675326745327645762354",
                         callbacks=[test_callback],
                         background_image="data/gui/base.png",
                         background_image_hover="data/gui/base.png",
                         background_image_click=None)
    pyggel.Newgui.Label(frame, "test:", background_image="data/gui/base.png", font_underline=True)
    pyggel.Newgui.Checkbox(frame, background_image="data/gui/check_open.png",
                           check_image="data/gui/check_closed.png")

    for i in xrange(10):
        pyggel.Newgui.Label(frame, "testing456", background_image="data/gui/base.png")

    pyggel.Newgui.Button(app, "Click me!:PXD", callbacks=[test_callback],
                         background_image="data/gui/base.png",
                         background_image_hover="data/gui/base.png",
                         background_image_click=None)
    pyggel.Newgui.Button(app, "Swap Apps!", callbacks=[lambda: swap_apps(newapp)],
                         background_image="data/gui/base.png",
                         background_image_hover="data/gui/base.png",
                         background_image_click=None)
    pyggel.Newgui.NewLine(app)

    for i in xrange(2):
        for i in xrange(random.randint(1, 2)):
            pyggel.Newgui.Label(app, "testing! 123", background_image="data/gui/base.png")
        pyggel.Newgui.NewLine(app, random.choice([0, 15]))

    pyggel.Newgui.Label(app, "Hey!", (0, 0), background_image="data/gui/base.png")
    pyggel.Newgui.Radio(app, options=["test", "34", "56"],
                        background_image="data/gui/base.png",
                        option_background_image="data/gui/check_open.png",
                        option_check_image="data/gui/check_closed.png")
    pyggel.Newgui.MultiChoiceRadio(app, options=["mc1", "mc2"],
                                    background_image="data/gui/base.png",
                                    option_background_image="data/gui/check_open.png",
                                    option_check_image="data/gui/check_closed.png")
    pyggel.Newgui.NewLine(app)
    pyggel.Newgui.Input(app, "test me...", background_image="data/gui/base.png")

    pyggel.Newgui.MoveBar(app, "TestWindow", background_image="data/gui/base.png", child=frame)
    window = pyggel.Newgui.Window(app, "P Window-take2!!!", (100,100), (100,100),
                                  background_image="data/gui/base.png",
                                  movebar_background_image="data/gui/base.png")
    pyggel.Newgui.Label(window, "Woot!:P")
    pyggel.Newgui.Menu(newapp, "Menu", options=["help", "test", "quit","2","3","4","Snazzlemegapoof!!!!",
                                             ["please work!", "1", "2", "3", "asfkjhsakfh",
                                              ["subagain!", "1", "2", "3"*10]]],
                       menu_background_image="data/gui/base.png",
                       background_image="data/gui/base.png",
                       background_image_hover="data/gui/base.png",
                       background_image_click="data/gui/base.png",
                       option_background_image="data/gui/base.png",
                       option_background_image_hover="data/gui/base.png",
                       option_background_image_click="data/gui/base.png",
                       callback=test_menu)
    pyggel.Newgui.Button(newapp, "Swap Back!", callbacks=[lambda: swap_apps(app)],
                         background_image="data/gui/base.png",
                         background_image_hover="data/gui/base.png",
                         background_image_click=None)

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())
        eh.update()
        if eh.quit:
            pyggel.quit()
            return None

        pyggel.view.clear_screen()
        scene.render()
        pyggel.view.refresh_screen()

main()
