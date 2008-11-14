from include import *

import mesh, view, image, camera, math3d, light, scene, font, geometry

def quit():
    view.clear_screen()
    glFlush()
    pygame.quit()

init = view.init

def get_events():
    return pygame.event.get()
