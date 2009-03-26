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
    pyggel.init(screen_size_2d=(600, 400))

    scene = pyggel.scene.Scene()

    eh = pyggel.event.Handler()
    app = pyggel.gui.App(eh)
    app.theme.load("data/gui/theme.py")
    newapp = pyggel.gui.App(eh)
    newapp.theme = app.theme
    app.activate() #first one ;)
    regfont = app.get_regfont("default")
    mefont = app.get_mefont("default")
    regfont.add_image(":P", pyggel.image.GridSpriteSheet("data/ar.png", (3,3)))
    mefont.add_image(":P", pyggel.image.GridSpriteSheet("data/ar.png", (3,3)))
    app.packer.packtype="center"
    scene.add_2d(app)
    scene.add_2d(newapp)

    frame = pyggel.gui.Frame(app, (500, 0), (140, 300), image_border=9)
    frame.packer.packtype = "wrap"

    pyggel.gui.Button(frame, "click!:P", callbacks=[test_callback],
                         font_underline=True)
    pyggel.gui.Button(frame, "click!124675326745327645762354",
                         callbacks=[test_callback],
                         background_image_click=None)
    pyggel.gui.Label(frame, "test:", font_underline=True)
    pyggel.gui.Checkbox(frame)

    for i in xrange(10):
        pyggel.gui.Label(frame, "testing456")

    pyggel.gui.Button(app, "Click me!:PXD", callbacks=[test_callback],
                         background_image_click=None)
    pyggel.gui.Button(app, "Swap Apps!", callbacks=[lambda: swap_apps(newapp)],
                         background_image_click=None)
    pyggel.gui.NewLine(app)

    for i in xrange(2):
        for i in xrange(random.randint(1, 2)):
            pyggel.gui.Label(app, "testing! 123")
        pyggel.gui.NewLine(app, random.choice([0, 15]))

    pyggel.gui.Label(app, "Hey!", (0, 0))
    pyggel.gui.Radio(app, options=["test", "34", "56"])
    pyggel.gui.MultiChoiceRadio(app, options=["mc1", "mc2"])
    pyggel.gui.NewLine(app)
    pyggel.gui.Input(app, "test me...")

    pyggel.gui.MoveBar(app, "TestWindow", child=frame)
    window = pyggel.gui.Window(app, "P Window-take2!!!", (100,100), (100,100))
    pyggel.gui.Label(window, "Woot!:P")
    pyggel.gui.Menu(window, "testing?", options=["1"*6]*5, callback=test_menu)
    pyggel.gui.Menu(newapp, "Menu", options=["help", "test", "quit","2","3","4","Snazzlemegapoof!!!!",
                                             ["please work!", "1", "2", "3", "asfkjhsakfh",
                                              ["subagain!", "1", "2", "3"*10]]],
                       callback=test_menu)
    pyggel.gui.Button(newapp, "Swap Back!", callbacks=[lambda: swap_apps(app)],
                         background_image_click=None)
    pyggel.gui.Icon(newapp, image="data/gui/smiley.gif")

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
