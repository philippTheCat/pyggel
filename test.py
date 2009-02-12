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

    img = pyggel.image.Image("data/tile_example.png", pos=(50, 50))
    img.colorize=(1,0,0,1)
    img2 = pyggel.image.Image("data/ar.png", pos=(50,0))
    img2.colorize=(1,1,1,0.5)
    img2sub = img2.sub_image((0,0), (15, 15))
    img2sub.colorize=(1, 0, 0, 1)
    img2sub.pos = (600, 400)
    img3d = []
    for x in xrange(10):
        img3d.append(pyggel.image.Image3D("data/tile_example.png",
                                          pos=(random.randint(-10, 10),
                                               random.randint(-10, 10),
                                               10)))

    font = pyggel.font.Font()
    img4 = font.make_text_image("Hello World: 2D", (255, 255, 0))
    img5 = font.make_text_image3D("Hello World: 3D", (0, 255, 255))
    img5.scale = 2

    img.blit(img2, (0, 0))

    obj = pyggel.mesh.OBJ("data/carrot.obj")
    obj2 = obj.copy()
    obj2.pos = (0,0,5)
    
    horse = pyggel.mesh.OBJ("data/mikkis_horse_v4.obj")

    box = pyggel.geometry.Cube(5, texture=[data.Texture("data/stickdude.png")]*6)
    box.pos = (-5, 0, 0)

    my_scene = pyggel.scene.Scene()
    my_scene.add_2d(img)
    my_scene.add_2d(img2)
    my_scene.add_2d(img2sub)
    my_scene.add_2d(img4)

    my_scene.add_3d(obj)
    my_scene.add_3d(obj2)
    my_scene.add_3d(horse)
    my_scene.add_3d(box)
    for i in img3d:
        my_scene.add_3d(i)
    my_scene.add_3d(img5)

    my_scene.add_light(my_light)

    clock = pygame.time.Clock()

    rot = 0

    last_hit = None

    meh = pyggel.event.Handler()
    meh.bind_to_event(" ", lambda a,b: pyggel.misc.save_screenshot("Test.png"))

    my_app = pyggel.gui.App(meh)
    my_app.mefont.add_smiley(":)", "data/stickdude.png")
    my_app.mefont.add_smiley(":P", img2sub)
    pyggel.gui.Label(my_app, "testy!!!")
    pyggel.gui.Label(my_app, "123!!!")
    pyggel.gui.Label(my_app, "testy!!!")
    pyggel.gui.Label(my_app, "123!!!")
    pyggel.gui.Label(my_app, "testy!!!")
    pyggel.gui.Label(my_app, "123!!!")
    pyggel.gui.Label(my_app, "testy!!!")
    pyggel.gui.Label(my_app, "123!!!")
    pyggel.gui.Label(my_app, "testy!!!")
    pyggel.gui.Label(my_app, "123!!!")
    pyggel.gui.Label(my_app, "testy!!!")
    pyggel.gui.Label(my_app, "123!!!")
    pyggel.gui.Label(my_app, "testy!!!")
    pyggel.gui.Label(my_app, "123!!!")
    pyggel.gui.Label(my_app, "testy!!!")
    pyggel.gui.Label(my_app, "123!!!")
    pyggel.gui.Label(my_app, "testy!!!")

    def test_callback():
        pyggel.gui.Label(my_app, "umm...:)...:P...")
    pyggel.gui.Button(my_app, "BUTTON!", callbacks=[test_callback])

    my_scene.add_2d(my_app)

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())

        meh.update()

        if meh.quit:
            pyggel.quit()
            return None
        if "left" in meh.mouse.hit:
            if img.get_rect().collidepoint(meh.mouse.get_pos()):
                if img.to_be_blitted:
                    img.clear_blits()
                else:
                    img.blit(img2, (0,0))

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

        rot += 1
        a,b,c = img.rotation
        c += 1
        img.rotation = a,b,c

        a,b,c = img2.rotation
        c -= 1
        img2.rotation = a,b,c

        img5.visible = not img5.visible

        pyggel.view.clear_screen()

        hit = my_scene.pick(pygame.mouse.get_pos(), camera).hit
        if hit:
            hit.colorize = (1, 0, 0, 1)
        if last_hit:
            if not hit == last_hit:
                last_hit.colorize = (1,1,1,1)
        last_hit = hit
        my_scene.render(camera)

        pyggel.view.refresh_screen()
main()
