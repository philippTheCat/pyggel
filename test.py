import pyggel
from pyggel import *

import random

def main():
    pyggel.view.init()
    pyggel.view.set_debug(False)

    my_light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)
##    camera = pyggel.camera.LookFromCamera((0,0,10))

    img = pyggel.image.Image("data/tile_example.png")
    img.colorize=(1,0,0,1)
    img2 = pyggel.image.Image("data/ar.png", pos=(50,0))
    img2.colorize=(1,1,1,0.5)
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

    box = pyggel.geometry.Cube(5, texture=[image.Texture("data/stickdude.png")]*6)
    box.pos = (-5, 0, 0)

    my_scene = pyggel.scene.Scene()
    my_scene.add_2d(img)
    my_scene.add_2d(img2)
    my_scene.add_2d(img4)
    my_scene.add_3d(obj)
    my_scene.add_3d(obj2)
    my_scene.add_3d(box)
    for i in img3d:
        my_scene.add_3d(i)
    my_scene.add_3d(img5)

    my_scene.add_light(my_light)

    clock = pygame.time.Clock()

    rot = 0

    last_hit = None

    while 1:
        clock.tick(999)
        print clock.get_fps()
        for event in pyggel.get_events():
            if event.type == QUIT:
                pyggel.quit()
                return None

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if img.get_rect().collidepoint(event.pos):
                        if img.to_be_blitted:
                            img.clear_blits()
                        else:
                            img.blit(img2, (0, 0))
            if event.type == KEYDOWN and event.key == K_SPACE:
                pyggel.misc.save_screenshot("Test.png")

        key = pygame.key.get_pressed()
        if key[K_LEFT]:
            camera.roty -= .5
        if key[K_RIGHT]:
            camera.roty += .5
        if key[K_UP]:
            camera.rotx -= .5
        if key[K_DOWN]:
            camera.rotx += .5
        if key[K_1]:
            camera.rotz -= .5
        if key[K_2]:
            camera.rotz += .5

        if key[K_EQUALS]:
            camera.distance -= .1
        if key[K_MINUS]:
            camera.distance += .1

        if key[K_a]:
            camera.posx -= .1
        if key[K_d]:
            camera.posx += .1
        if key[K_s]:
            camera.posz -= .1
        if key[K_w]:
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
