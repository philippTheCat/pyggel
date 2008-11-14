import pyggel
from pyggel import *

def main():
    pyggel.init()

    camera1 = pyggel.camera.LookFromCamera((0,0,10))
    camera2 = pyggel.camera.LookAtCamera((0,0,0), distance=10)
    camera = camera1
    font = pyggel.font.Font()
    img = font.make_text_image3D("Hello World: 3D", (255, 255, 0))
    img.scale = 5
    img2 = font.make_text_image3D("Hello World: 3D X2!!!", (0, 255, 255))
    img2.pos = (0, 3, 0)

    box = pyggel.geometry.Cube(5)
    box.pos=(0,0,0)

    mscene = pyggel.scene.Scene()
    mscene.add_3d_facing(img)
    mscene.add_3d(box)
    mscene.add_3d_facing(img2)

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
        print clock.get_fps()

        for event in pyggel.get_events():
            if event.type == QUIT:
                pyggel.quit()
                return None

            if event.type == KEYDOWN and event.key == K_RETURN:
                if camera == camera1:
                    camera = camera2
                else:
                    camera = camera1

        key = pygame.key.get_pressed()
        if key[K_m]:
            if key[K_LEFT]:
                camera.posx -= .1
            if key[K_RIGHT]:
                camera.posx += .1
            if key[K_UP]:
                camera.posy += .1
            if key[K_DOWN]:
                camera.posy -= .1
            if key[K_MINUS]:
                camera.posz += .1
            if key[K_EQUALS]:
                camera.posz -= .1
        elif key[K_r]:
            if key[K_LEFT]:
                camera.roty -= .25
            if key[K_RIGHT]:
                camera.roty += .25
            if key[K_UP]:
                camera.rotx -= .25
            if key[K_DOWN]:
                camera.rotx += .25
            if key[K_MINUS]:
                camera.rotz -= .25
            if key[K_EQUALS]:
                camera.rotz += .25

        box.pos = camera2.get_pos()

        mscene.render(camera)
        pyggel.view.refresh_screen()

main()
