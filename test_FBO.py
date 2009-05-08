import pyggel
from pyggel import *

import random

def main():
    pyggel.view.init(screen_size=(800,600), screen_size_2d=(640, 480))
    pyggel.view.set_debug(False)

    my_light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)
    fbo_camera = pyggel.camera.LookAtCamera((0,0,0), distance=5)
    fbo_camera.rotx = 90

    obj = pyggel.mesh.OBJ("data/bird_plane.obj", False)
    obj.scale = .25

    box = pyggel.geometry.Cube(2.5, texture=None)
    box.pos=(-3, 0, 0)

    box2 = pyggel.geometry.Cube(2.5, texture=None)
    box2.pos=(3, 0, 0)

    my_scene = pyggel.scene.Scene()
    fbo_scene = pyggel.scene.Scene()
    fbo_scene.render_buffer = pyggel.data.FrameBuffer(clear_color=(1,1,1))

    tbo_scene = pyggel.scene.Scene()
    tbo_scene.render_buffer = pyggel.data.TextureBuffer(clear_color=(1,1,0))

    print fbo_scene.render_buffer.worked, tbo_scene.render_buffer.worked

    fbo_scene.add_3d(obj)
    tbo_scene.add_3d(obj)
    my_scene.add_3d((box, box2, obj))

    my_scene.add_light(my_light)
    fbo_scene.add_light(my_light)
    tbo_scene.add_light(my_light)

    clock = pygame.time.Clock()

    meh = pyggel.event.Handler()
    meh.bind_to_event(" ", lambda a,b: pyggel.misc.save_screenshot("Test.png"))

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())

        meh.update()

        if meh.quit:
            pyggel.quit()
            return None

        if K_LEFT in meh.keyboard.active:
            camera.roty -= .5
        if K_RIGHT in meh.keyboard.active:
            camera.roty += .5
        if K_DOWN in meh.keyboard.active:
            camera.rotx -= .5
        if K_UP in meh.keyboard.active:
            camera.rotx += .5
        if K_1 in meh.keyboard.active:
            camera.rotz -= .5
        if "2" in meh.keyboard.active: #just to throw you off ;)
            camera.rotz += .5

        if "=" in meh.keyboard.active:
            camera.distance -= .1
        if "-" in meh.keyboard.active:
            camera.distance += .1

        if "a" in meh.keyboard.active:
            camera.posx -= .1
        if K_d in meh.keyboard.active:
            camera.posx += .1
        if K_s in meh.keyboard.active:
            camera.posz -= .1
        if K_w in meh.keyboard.active:
            camera.posz += .1

        fbo_camera.rotz += 1

        pyggel.view.clear_screen()

        fbo_scene.render(fbo_camera)

        tbo_scene.render(fbo_camera)

        box.texture = fbo_scene.render_buffer.texture
        box2.texture = tbo_scene.render_buffer.texture

        my_scene.render(camera)

        pyggel.view.refresh_screen()
main()
