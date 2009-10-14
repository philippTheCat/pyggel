#test pyggel.font.FastFont
import pyggel
from pyggel import *

import random

def main():
    pyggel.init()

    pyggel.view.set_debug(False)

    eh = pyggel.event.Handler()

    clock = pygame.time.Clock()

    i = pygame.image.load("data/ar.png")

    mefont = pyggel.font.MEFont(None, 32)
    rfont = pyggel.font.RFont(None, 32)

    t1 = mefont.make_text_image("test")
    t2 = rfont.make_text_image("test")

    image = pyggel.image.Image("data/ar.png")

    while 1:
##        clock.tick(999)
##        pyggel.view.set_title("FPS: %s"%clock.get_fps())
##        eh.update()
##        if eh.quit:
##            pyggel.quit()
##            return None

        ##tests:
##        pyggel.data.BlankTexture().bind()
##        pyggel.data.Texture("data/ar.png")
##        pyggel.data.Texture(i)
##        pyggel.image.Image("data/ar.png")
##        t1.text = "test"
##        t2.text = str(f)
        image.copy()

main()

