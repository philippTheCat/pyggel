from include import *

import load_obj, view, image, camera, math3d, light, scene

def quit():
    view.clear_screen()
    glFlush()
    pygame.quit()

def get_events():
    return pygame.event.get()
