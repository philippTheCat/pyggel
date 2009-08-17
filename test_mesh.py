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
    camera.roty = 180

    obj = pyggel.mesh.OBJ("data/bird_plane.obj")
    obj.scale = .5

    Tree = pyggel.mesh.ChildTree()
    root = "cylinder1"
    tail = "sphere2"
    head = "sphere2_copy3"
    wings = "cube4"
    Tree.add_object(root)
    Tree.add_object(head, root)
    Tree.add_object(tail, root)
    Tree.add_object(wings, root)
    Tree.root = root #important!

    Flap = pyggel.mesh.FramedAnimationCommand(10,
                    #mesh    pos      rot     scale
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

    ani = pyggel.mesh.FramedAnimation(obj, Tree, {"flap":Flap})
    ani.action = "flap"
    ani.pos = (-3,0,0)

    Flap2 = pyggel.mesh.InterpAnimationCommand(
                    [(wings,(0,0,0),(0,0,30),(0,0,0),0,.5),
                     (wings,(0,0,0),(0,0,-60),(0,0,0),.5,1.5),
                     (wings,(0,0,0),(0,0,30),(0,0,0),1.5,2),

##                     (root,(0,0,0),(0,0,30),(0,0,0),0,.5),
##                     (root,(0,0,0),(0,0,-60),(0,0,0),.5,1.5),
##                     (root,(0,0,0),(0,0,30),(0,0,0),1.5,2),

                     (tail,(0,0,1),(0,0,0),(0,0,1),0,1),
                     (tail,(0,0,-1),(0,0,0),(0,0,-1),1,2),

                     (head,(0,0,0),(0,0,360),(0,1,0),0,1),
                     (head,(0,0,0),(0,0,-360),(0,-1,0),1,2)],
                                        2)

    ani2 = pyggel.mesh.InterpAnimation(obj, Tree, {"flap":Flap2})
    ani2.action = "flap"
    ani2.pos = (3,0,0)

    exp = pyggel.mesh.Exploder(obj.copy(), .025, 250)

    my_scene = pyggel.scene.Scene()
    my_scene.pick = True
    my_scene.add_3d(obj)
    my_scene.add_3d(ani)
    my_scene.add_3d(ani2)
    my_scene.add_3d(exp)

    my_scene.add_light(my_light)

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

        pyggel.view.clear_screen()

        my_scene.render(camera)

        mpx, mpy = pyggel.view.screen.get_mouse_pos()

        pyggel.view.refresh_screen()
main()
