from include import *

import mesh, view, image, camera, math3d, light, scene, font

def quit():
    view.clear_screen()
    glFlush()
    pygame.quit()

def get_events():
    return pygame.event.get()
