import pyggel
from pyggel import *

def main():
    pyggel.view.init()

    my_light = pyggel.light.Light((0,0,1), (0,0,0,0),
                                  (1,1,1,1), (1,1,1,1),
                                  (0,0,0), True)
    light_group = pyggel.light.LightGroup()
    light_group.add_light(my_light)
    my_light.enable(GL_LIGHT0)

    camera = pyggel.camera.LookAtCamera((0,0,-5), distance=10)
##    camera = pyggel.camera.LookFromCamera((0,0,10))

    img = pyggel.image.Image("data/tile_example.png")
    img2 = pyggel.image.Image("data/ar.png")

    img.blit(img2, (0, 0))

    im = img

    obj = pyggel.load_obj.OBJ("data/carrot.obj")

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
                    if im.get_rect().collidepoint(event.pos):
                        if im == img:
                            im = img2
                        else:
                            im = img

            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    camera.roty -= 15
                if event.key == K_RIGHT:
                    camera.roty += 15
                if event.key == K_UP:
                    camera.rotx += 15
                if event.key == K_DOWN:
                    camera.rotx -= 15

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

        rot += 1

        pyggel.view.clear_screen()
        pyggel.view.set3d()
        camera.push()
        obj.render((camera.get_pos()), (rot, rot, 0))
        obj.render((0,0,-10))
        camera.pop()
        pyggel.view.set2d()
        im.render((0, 0))
        img2.render((50, 0))
        img2.rotate((0,0,1))
        im.rotate((0,0,-1))

        pyggel.view.refresh_screen()

main()
