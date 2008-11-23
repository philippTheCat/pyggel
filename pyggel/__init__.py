"""
pyggle.__init__
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *

import mesh, view, image, camera, math3d, light
import scene, font, geometry, misc, picker

def quit():
    for i in image._all_textures: del i
    for i in image._all_images: del i
    for i in image._all_3d_images: del i
    image._all_textures = {}
    image._all_images = {}
    image._all_3d_images = {}
    view.clear_screen()
    glFlush()
    pygame.quit()

init = view.init

def get_events():
    return pygame.event.get()
