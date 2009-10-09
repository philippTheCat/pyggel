#test pyggel.font.FastFont
import pyggel
from pyggel import *

import random

def main():
    pyggel.init()

    pyggel.view.set_debug(False)

    scene = pyggel.scene.Scene()
    scene.camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)

    eh = pyggel.event.Handler()

    font = pyggel.font.FastFont()
    s = "Hello World! Testing-123 Come on!"
    c = []
    r = pyggel.misc.randfloat
    for i in s:
        c.append((r(0.2,1), r(0.2,1), r(0.2,1), 1))
    text = font.make_text_image2D(s, color=c, italic=True, bold=True, linewrap=150)

    text3d = font.make_text_image3D(s, color=c, italic=True, bold=True, linewrap=150)

    scene.add_2d(text)
    scene.add_3d(text3d)

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())
        eh.update()
        if eh.quit:
            pyggel.quit()
            return None

        if K_LEFT in eh.keyboard.active:
            scene.camera.roty -= .5
        if K_RIGHT in eh.keyboard.active:
            scene.camera.roty += .5
        if K_DOWN in eh.keyboard.active:
            scene.camera.rotx -= .5
        if K_UP in eh.keyboard.active:
            scene.camera.rotx += .5

        if "=" in eh.keyboard.active:
            scene.camera.distance -= .1
        if "-" in eh.keyboard.active:
            scene.camera.distance += .1

        if "a" in eh.keyboard.active:
            scene.camera.posx -= .1
        if K_d in eh.keyboard.active:
            scene.camera.posx += .1
        if K_s in eh.keyboard.active:
            scene.camera.posz -= .1
        if K_w in eh.keyboard.active:
            scene.camera.posz += .1

        text.rotate(0,0,0.2)

        pyggel.view.clear_screen()
        scene.render()#camera)
        pyggel.view.refresh_screen()

main()
