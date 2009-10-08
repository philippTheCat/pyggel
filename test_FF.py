#test pyggel.font.FastFont
import pyggel
from pyggel import *

import random

def test_callback():
    print "woo!"
def test_menu(item):
    print item
def swap_apps(new):
    new.activate()

def main():
    pyggel.init()#screen_size_2d=(600, 400))
    glDisable(GL_CULL_FACE)

    pyggel.view.set_debug(False)

    scene = pyggel.scene.Scene()
    camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)

    eh = pyggel.event.Handler()

    font = pyggel.font.FastFont()
    s = "Hello World!\nTesting-123\nCome on!"
    c = []
    r = pyggel.misc.randfloat
    for i in s:
        c.append((r(0.2,1), r(0.2,1), r(0.2,1), 1))
    text = font.make_text_image2D(s, color=c, italic=True, bold=True)

##    text.rotate(0,0,45)
    text.move(100,100,0)

    scene.add_2d(text)

    clock = pygame.time.Clock()

    eh.bind_to_event("keydown", lambda key,ident:text.set_text(ident))

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())
        eh.update()
        if eh.quit:
            pyggel.quit()
            return None

        text.rotate(0,0,0.2)

        pyggel.view.clear_screen()
        scene.render(camera)
        pyggel.view.refresh_screen()

main()
