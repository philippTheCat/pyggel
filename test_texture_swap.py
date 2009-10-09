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

    font = pyggel.font.MEFont()
    font3d = pyggel.font.Font3D()
    img4 = font.make_text_image("Hello World: 2D", (1, 1, 0), underline=True, italic=True, bold=True)
    img4.pos = (50,50)
    img5 = font3d.make_text_image("Hello World: 3D", (0, 1, 1))
    img5.scale = 2

    img6 = pyggel.image.GIFImage("data/smiley.gif", pos=(150, 150))
    img7 = pyggel.image.GIFImage3D("data/smiley.gif", pos=(0,0,1))

    pyggel.view.set_cursor(pyggel.image.SpriteSheet("data/ar.png",
                                    [(0,0,16,16), (16,0,16,16), (32,0,16,16), (16,0,16,16)],
                                    100),
                           True)

    img.blit(img2, (0, 0))

    obj = pyggel.mesh.OBJ("data/bird_plane.obj")
    obj.scale = .5
    obj2 = obj.copy()
    obj2.pos = (0,0,5)

    box = pyggel.geometry.Cube(5, texture=data.Texture("data/stickdude.png"))
    box.pos = (-5, 0, 0)

    my_scene = pyggel.scene.Scene()
    my_scene.camera = camera
    my_scene.pick = True
    my_scene.add_2d(img)
    my_scene.add_2d(img2)
    my_scene.add_2d(img2sub)
    my_scene.add_2d(img4)
    my_scene.add_2d(img6)

    my_scene.add_3d(obj)
    my_scene.add_3d(obj2)
    my_scene.add_3d(box)
    my_scene.add_3d(img3d)
    my_scene.add_3d(img5)
    my_scene.add_3d(img7)

    my_scene.add_light(my_light)

    clock = pygame.time.Clock()

    rot = 0

    last_hit = None

    meh = pyggel.event.Handler()
    meh.bind_to_event(" ", lambda a,b: pyggel.misc.save_screenshot("Test.png"))

    to_swap = [obj, box, img5]+img3d

    swap_to_image = pyggel.data.BlankTexture(color=(0,1,0,.75))
    swap_material = pyggel.data.Material("blank")
    swap_material.set_color((0,1,0,.75))
    for i in to_swap: #here are our objects we want to change around...
        if isinstance(i, pyggel.mesh.BasicMesh):
            #needs a little different from others!
            new = []
            for x in i.objs:
                a = x.copy()
                a.material = swap_material
                new.append(a)
            i.swap_texs = [i.objs, new] #this value can be whatever you want!
        else:
            i.swap_texs = [i.texture, swap_to_image]
        i.current_swap_tex = 0 #because it is!
        #now the rest will be handled in teh main loop!

    last_time = time.time()
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

        rot += 1
        a,b,c = img.rotation
        c += 1
        img.rotation = a,b,c

        a,b,c = img2.rotation
        c -= 1
        img2.rotation = a,b,c

        if time.time() - last_time >= 1: #limit to every second
            last_time = time.time()
            for i in to_swap: #time to apply those texture swaps!
                i.current_swap_tex = abs(i.current_swap_tex - 1)
                if isinstance(i, pyggel.mesh.BasicMesh):
                    i.objs = i.swap_texs[i.current_swap_tex]
                else:
                    i.texture = i.swap_texs[i.current_swap_tex]

        pyggel.view.clear_screen()

        hit = my_scene.render()#camera)
        if last_hit:
            last_hit.colorize = (1,1,1,1)
        if hit:
            hit.colorize = (1, 0, 0, 1)
        last_hit = hit

        mpx, mpy = pyggel.view.screen.get_mouse_pos()

        pyggel.view.refresh_screen()
main()
