import pyggel
from pyggel import *

import random

def test_callback():
    print "woo!"
def test_menu(item):
    print item

def main():
    pyggel.init()

    scene = pyggel.scene.Scene()

    eh = pyggel.event.Handler()
    app = pyggel.Newgui.App(eh)
    app.mefont.add_smiley(":P", pyggel.image.GridSpriteSheet("data/ar.png", (3,3)))
    app.packer.packtype="center"
    scene.add_2d(app)

    frame = pyggel.Newgui.Frame(app, (500, 0), (140, 300), image="data/gui/base.png")
    frame.packer.packtype = "wrap"

    pyggel.Newgui.Button(frame, "click!", callbacks=[test_callback], images=["data/gui/base.png", "data/gui/base.png", None])
    pyggel.Newgui.Button(frame, "click!124675326745327645762354",
                         callbacks=[test_callback], images=["data/gui/base.png", "data/gui/base.png", None])
    pyggel.Newgui.Label(frame, "test:", image="data/gui/base.png")
    pyggel.Newgui.Checkbox(frame, images=["data/gui/check_open.png", "data/gui/check_closed.png"])

    for i in xrange(10):
        pyggel.Newgui.Label(frame, "testing456", image="data/gui/base.png")

    pyggel.Newgui.Button(app, "Click me!", callbacks=[test_callback],
                         images=["data/gui/base.png", "data/gui/base.png", None])
    pyggel.Newgui.NewLine(app)

    for i in xrange(2):
        for i in xrange(random.randint(1, 2)):
            pyggel.Newgui.Label(app, "testing!123", image="data/gui/base.png")
        pyggel.Newgui.NewLine(app, random.choice([0, 15]))

    pyggel.Newgui.Label(app, "Hey!", (0, 0), image="data/gui/base.png")
    pyggel.Newgui.Radio(app, options=["test", "34", "56"], images=["data/gui/base.png",
                                                                   "data/gui/check_open.png",
                                                                   "data/gui/check_closed.png"])
    pyggel.Newgui.MultiChoiceRadio(app, options=["mc1", "mc2"], images=["data/gui/base.png",
                                                                        "data/gui/check_open.png",
                                                                        "data/gui/check_closed.png"])
    pyggel.Newgui.NewLine(app)
    pyggel.Newgui.Input(app, "test me...", image="data/gui/base.png")

    pyggel.Newgui.MoveBar(app, "TestWindow", image="data/gui/base.png", child=frame)
    window = pyggel.Newgui.Window(app, "P Window-take2!!!", (100,100), (100,100),
                                  images=["data/gui/base.png", "data/gui/base.png"])
    pyggel.Newgui.Label(window, "Woot!:P", compile_text=False)
    pyggel.Newgui.Menu(app, "Menu", options=["help", "test", "quit","2","3","4","Snazzlemegapoof!!!!",
                                             ["please work!", "1", "2", "3", "asfkjhsakfh",
                                              ["subagain!", "1", "2", "3"*10]]],
                       images=["data/gui/base.png"]*4, callback=test_menu)

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
