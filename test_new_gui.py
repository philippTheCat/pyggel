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
    app.packer.packtype="center"
    scene.add_2d(app)

    pyggel.Newgui.Button(app, "Click me!", callbacks=[test_callback])
    pyggel.Newgui.NewLine(app)

    for i in xrange(10):
        for i in xrange(random.randint(0, 4)):
            pyggel.Newgui.Label(app, "testing!123")
        pyggel.Newgui.NewLine(app, random.choice([0, 15]))

    pyggel.Newgui.Label(app, "Hey!", (0, 0))

    while 1:
        eh.update()
        if eh.quit:
            pyggel.quit()
            return None

        pyggel.view.clear_screen()
        scene.render()
        pyggel.view.refresh_screen()

main()
