import pyggel
from pyggel import *

import random, time

def main():
    pyggel.view.init(screen_size=(800,600), screen_size_2d=(640, 480))
    pyggel.view.set_debug(False)

    my_light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)
    camera.roty = 180

    obj = pyggel.mesh.OBJ("data/bird_plane.obj")
    root = obj.get_obj_by_name("cylinder1")
    tail = obj.get_obj_by_name("sphere2")
    head = obj.get_obj_by_name("sphere2_copy3")
    wings = obj.get_obj_by_name("cube4")

    skel = pyggel.mesh.Skeleton()
    skel.add_bone(root.name, (0,0,root.side("back")), (0,0,root.side("front")))
    skel.add_bone(tail.name, (0,0,tail.side("front")), (0,0,tail.side("back")), root.name)
    skel.add_bone(head.name, (0,0,head.side("back")), (0,0,head.side("front")), root.name, 0.25)
    skel.add_bone(wings.name, (wings.side("left"),0,0), (wings.side("right"),0,0), root.name, 0.5)

    action = pyggel.mesh.Action(2, [pyggel.mesh.RotateTo(wings.name, (0,0,45),0,.5),
                        pyggel.mesh.RotateTo(wings.name, (0,0,-45),.5,1.5),
                        pyggel.mesh.RotateTo(wings.name, (0,0,0),1.5,2),
                        pyggel.mesh.ScaleTo(tail.name, (1.25,1.25,1.25), 0, 1),
                        pyggel.mesh.ScaleTo(tail.name, (1,1,1), 1, 2),
                        pyggel.mesh.RotateTo(head.name, (0,15,0),0,.25),
                        pyggel.mesh.RotateTo(head.name, (0,-15,0),.25,.75),
                        pyggel.mesh.RotateTo(head.name, (0,0,0),.75,1),

                        pyggel.mesh.RotateTo("weapon_right", (0,0,-45),0,.5),
                        pyggel.mesh.RotateTo("weapon_right", (0,0,45),.5,1.5),
                        pyggel.mesh.RotateTo("weapon_right", (0,0,0),1.5,2),
                        pyggel.mesh.RotateTo("weapon_left", (0,0,-45),0,.5),
                        pyggel.mesh.RotateTo("weapon_left", (0,0,45),.5,1.5),
                        pyggel.mesh.RotateTo("weapon_left", (0,0,0),1.5,2)])
    head_left = pyggel.mesh.Action(1, [pyggel.mesh.RotateTo(head.name, (0,45,0),0,1)])
    head_right = pyggel.mesh.Action(1, [pyggel.mesh.RotateTo(head.name, (0,-45,0), 0,1)])
    head_up = pyggel.mesh.Action(1, [pyggel.mesh.RotateTo(head.name, (45,0,0),0,1)])
    head_down = pyggel.mesh.Action(1, [pyggel.mesh.RotateTo(head.name, (-45,0,0),0,1)])
    head_test = pyggel.mesh.Action(5, [pyggel.mesh.RotateTo(head.name, (0,0,45),0,1),
                           pyggel.mesh.RotateTo(head.name, (0,-45,0),2,3),
                           pyggel.mesh.RotateTo(head.name, (0,0,0),4,5),
                           pyggel.mesh.RotateTo(tail.name, (0,0,360), 0,5),
                           pyggel.mesh.RotateTo(wings.name, (0,0,720),0,5)])
    ani = pyggel.mesh.Animation(obj, skel, {"1":head_left,
                                "2":head_right,
                                "3":head_up,
                                "4":head_down,
                                "5":action,
                                "6":head_test})

    #Let's make some connections here:
    new_obj = wings.copy()
    new_obj.name = "weapon_right"
    skel.add_bone(new_obj.name, (wings.side("right"),0,0), (wings.side("right")+new_obj.side("width"),0,0), wings.name)
    ani.mesh.objs.append(new_obj)
    new_obj2 = wings.copy()
    new_obj2.name = "weapon_left"
    skel.add_bone(new_obj2.name, (wings.side("left"),0,0), (wings.side("left")-new_obj2.side("width"),0,0), wings.name)
    ani.mesh.objs.append(new_obj2)

    new_obj3 = wings.copy()
    new_obj3.name = "weapon_right_right"
    skel.add_bone(new_obj3.name, (wings.side("right")+new_obj3.side("width"),0,0), (wings.side("right")+new_obj3.side("width")+new_obj.side("width"),0,0), new_obj.name)
    ani.mesh.objs.append(new_obj3)
    new_obj4 = wings.copy()
    new_obj4.name = "weapon_left_left"
    skel.add_bone(new_obj4.name, (wings.side("left")-new_obj4.side("width"),0,0), (wings.side("left")-new_obj2.side("width")-new_obj4.side("width"),0,0), new_obj2.name)
    ani.mesh.objs.append(new_obj4)

    ani2 = ani.copy()
    ani2.do("5", True)
    ani2.pos = (0,0,-10)

    clock = pygame.time.Clock()

    meh = pyggel.event.Handler()
    meh.bind_to_event(" ", lambda a,b: pyggel.misc.save_screenshot("Test.png"))

    last = None

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

        nums = ("1", "2", "3", "4", "5", "6")
        for i in nums:
            if i in meh.keyboard.hit:
                ani.do(i, False)

        pyggel.view.clear_screen()

        pyggel.view.set3d()
        camera.push()

        ani.render()
        ani2.render()

        camera.pop()
        pyggel.view.refresh_screen()
main()
