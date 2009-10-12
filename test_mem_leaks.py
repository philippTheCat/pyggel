#test pyggel.font.FastFont
import pyggel
from pyggel import *

import random

def main():
    pyggel.init()

    pyggel.view.set_debug(False)

    eh = pyggel.event.Handler()

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())
        eh.update()
        if eh.quit:
            pyggel.quit()
            return None

        pyggel.data.BlankTexture().bind()

main()
