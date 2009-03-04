import pyggel
from pyggel import *

import random

def test_callback():
    print "woo!"

def main():
    pyggel.init()

    scene = pyggel.scene.Scene()

    eh = pyggel.event.Handler()
    app = pyggel.Newgui.App(eh)
    app.mefont.add_smiley(":P", pyggel.image.GridSpriteSheet("data/ar.png", (3,3)))
    app.packer.packtype="center"
    scene.add_2d(app)

    frame = pyggel.Newgui.Frame(app, (500, 0), (140, 300), "data/gui.png")
    frame.packer.packtype = "wrap"

    pyggel.Newgui.Button(frame, "click!", callbacks=[test_callback], background="data/gui.png")
    pyggel.Newgui.Button(frame, "click!124675326745327645762354",
                         callbacks=[test_callback], background="data/gui.png")
    pyggel.Newgui.Label(frame, "test:", background="data/gui.png")
    pyggel.Newgui.Checkbox(frame, background="data/gui.png")

    for i in xrange(10):
        pyggel.Newgui.Label(frame, "testing456", background="data/gui.png")

    pyggel.Newgui.Button(app, "Click me!", callbacks=[test_callback],
                         background="data/gui.png")
    pyggel.Newgui.NewLine(app)

    for i in xrange(5):
        for i in xrange(random.randint(1, 3)):
            pyggel.Newgui.Label(app, "testing!123", background="data/gui.png")
        pyggel.Newgui.NewLine(app, random.choice([0, 15]))

    pyggel.Newgui.Label(app, "Hey!", (0, 0), background="data/gui.png")
    pyggel.Newgui.Radio(app, options=["test", "34", "56"], background="data/gui.png")
    pyggel.Newgui.MultiChoiceRadio(app, options=["mc1", "mc2"], background="data/gui.png")
    pyggel.Newgui.NewLine(app)
    pyggel.Newgui.Input(app, "test me...", background="data/gui.png")

    while 1:
        eh.update()
        if eh.quit:
            pyggel.quit()
            return None

        pyggel.view.clear_screen()
        scene.render()
        pyggel.view.refresh_screen()

main()
