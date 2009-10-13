#test pyggel.font.FastFont
import pyggel
from pyggel import *

import random

def main():
    pyggel.init()

    pyggel.view.set_debug(False)

    eh = pyggel.event.Handler()

    clock = pygame.time.Clock()

    mefont = pyggel.font.MEFont(None, 32)
    rfont = pyggel.font.RFont(None, 32)

    t1 = mefont.make_text_image("test")
    t2 = rfont.make_text_image("test")

    f = 0

    while 1:
        f += 1
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())
        eh.update()
        if eh.quit:
            pyggel.quit()
            return None

        ##Passed tests:
##        pyggel.data.BlankTexture().bind()
##        t1.text = str(f)
##        pyggel.data.Texture("data/ar.png")

        ##Failed tests:
##        pyggel.image.Image("data/ar.png")
##        t2.text = str(f)

main()
