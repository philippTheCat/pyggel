import pyggel
from pyggel import *

import random

def main():
    pyggel.view.init()

    my_light = pyggel.light.Light((0,0,1), (0,0,0,0),
                                  (1,1,1,1), (1,1,1,1),
                                  (0,0,0), True)
    light_group = pyggel.light.LightGroup()
    light_group.add_light(my_light)
    my_light.enable(GL_LIGHT0)

    camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)
##    camera = pyggel.camera.LookFromCamera((0,0,10))

    img = pyggel.image.Image("data/tile_example.png")
    img2 = pyggel.image.Image("data/ar.png", pos=(50,0))
    img3d = []
    for x in xrange(10):
        img3d.append(pyggel.image.Image3D("data/tile_example.png",
                                          pos=(random.randint(-10, 10),
                                               random.randint(-10, 10),
                                               -10)))

    img.blit(img2, (0, 0))

    obj = pyggel.load_obj.OBJ("data/carrot.obj")

    my_scene = pyggel.scene.Scene()
    my_scene.add_2d(img)
    my_scene.add_2d(img2)
    my_scene.add_3d(obj)
    for i in img3d:
        my_scene.add_3d_facing(i)

    clock = pygame.time.Clock()

    rot = 0

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

            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    camera.roty -= 15
                if event.key == K_RIGHT:
                    camera.roty += 15
                if event.key == K_UP:
                    camera.rotx += 15
                if event.key == K_DOWN:
                    camera.rotx -= 15
                if event.key == K_1:
                    camera.rotz -= 15
                if event.key == K_2:
                    camera.rotz += 15

                if event.key == K_EQUALS:
                    camera.distance -= 1
                if event.key == K_MINUS:
                    camera.distance += 1

                if event.key == K_a:
                    camera.posx -= .25
                if event.key == K_d:
                    camera.posx += .25
                if event.key == K_w:
                    camera.posz -= .25
                if event.key == K_s:
                    camera.posz += .25
                obj.pos = camera.get_pos()

        rot += 1
        img.rotate((0,0,1))
        img2.rotate((0,0,-1))
        my_scene.render(camera)

        pyggel.view.refresh_screen()
main()
