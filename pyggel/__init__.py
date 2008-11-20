"""
pyggle.__init__
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *

import mesh, view, image, camera, math3d, light, scene, font, geometry, misc

def quit():
    view.clear_screen()
    glFlush()
    pygame.quit()

init = view.init

def get_events():
    return pygame.event.get()
