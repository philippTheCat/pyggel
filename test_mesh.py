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

    obj = pyggel.mesh.OBJ("data/bird_plane.obj")
    obj.scale = .5
    print obj.get_names()

    Tree = pyggel.mesh.ChildTree()
    root = "cylinder1"
    head = "sphere2"
    tail = "sphere2_copy3"
    wings = "cube4"
    Tree.add_object(root)
    Tree.add_object(head, root)
    Tree.add_object(tail, root)
    Tree.add_object(wings, root)

    Flap = pyggel.mesh.AnimationCommand(10,
                    [{wings:[(0,0,0),(0,0,0),(1,1,1)]},
                     {wings:[(0,0,0),(0,0,10),(1,1,1)]},
                     {wings:[(0,0,0),(0,0,20),(1,1,1)]},
                     {wings:[(0,0,0),(0,0,30),(1,1,1)]},
                     {wings:[(0,0,0),(0,0,40),(1,1,1)]},

                     {wings:[(0,0,0),(0,0,0),(1,1,1)]},
                     {wings:[(0,0,0),(0,0,-10),(1,1,1)]},
                     {wings:[(0,0,0),(0,0,-20),(1,1,1)]},
                     {wings:[(0,0,0),(0,0,-30),(1,1,1)]},
                     {wings:[(0,0,0),(0,0,-40),(1,1,1)]}],
                                        0.1)

    ani = pyggel.mesh.Animation(obj, Tree, {"flap":Flap})
    ani.action = "flap"

    my_scene = pyggel.scene.Scene()
    my_scene.pick = True
##    my_scene.add_3d(obj)
    my_scene.add_3d(ani)

    my_scene.add_light(my_light)

    clock = pygame.time.Clock()

    rot = 0

    last_hit = None

    meh = pyggel.event.Handler()
    meh.bind_to_event(" ", lambda a,b: pyggel.misc.save_screenshot("Test.png"))

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())

        meh.update()

        if meh.quit:
            pyggel.quit()
            return None
        if "left" in meh.mouse.hit:
            if img.get_rect().collidepoint(pyggel.view.screen.get_mouse_pos2d()):
                if img.to_be_blitted:
                    img.clear_blits()
                else:
                    img.blit(img2, (0,0))
        if "right" in meh.mouse.hit:
            cur = view.screen.cursor
            if cur.running:
                cur.pause()
            else:
                cur.play()

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

        pyggel.view.clear_screen()

        hit = my_scene.render(camera)
        if last_hit:
            last_hit.outline = False
        if hit:
            hit.outline = True
        last_hit = hit

        mpx, mpy = pyggel.view.screen.get_mouse_pos()

        pyggel.view.refresh_screen()
main()
