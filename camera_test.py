import pyggel
from pyggel import *

def main():
    pyggel.init()

##    pyggel.view.set_lighting(False)

    light = pyggel.light.Light((0,0,1), (0,0,0,0),
                                  (1,1,1,1), (1,1,1,1),
                                  (0,0,0), True)

    camera1 = pyggel.camera.LookFromCamera((0,0,-10))
    camera2 = pyggel.camera.LookAtCamera((0,0,5), distance=10)
    camera = camera1
    font = pyggel.font.Font(None, 32)
    img = font.make_text_image3D("Hello\nWorld: 3D", (1, 1, 0, 1))
    img.scale = 5
    img2 = font.make_text_image3D("Hello World: 3D X2!!!", (0, 1, 1, 1))
    img2.pos = (0, .7, 0)
    img3 = img2.copy()
    img3.pos = (0, 0, 0)
    img4 = font.make_text_image3D("Testy...123...", (0, 1, 0, 1))
    img4.pos = (0, -1, 0)
    img5 = img4.copy()

    del img5
    img5 = img4.copy()
    img5.colorize = (1, 0, 0, .5)
    img5.pos = (0, .1, 0)

    text = font.make_text_image("ARG!!!!", (1, 0, 0, 1))
    text2 = text.copy()
    text2.pos = (0,75)

    font2 = pyggel.font.MEFont(None, 32)
    text3 = font2.make_text_image("Testing -\n1, 2, 3", (0, 0, 1, 1))

    box = pyggel.geometry.Cube(5, texture=[image.Texture("data/ar.png")]*6)
    box.pos = (0,0,5)
    box.rotation = list(box.rotation)
    sphere = pyggel.geometry.Sphere(5, texture=image.Texture("data/ar.png"))
    sphere.pos = (10, 0, 5)

    emitter = particle.Emitter3D(particle.Fire, (0, 0, -2))
    emitter.behavior.image = image.Image3D("data/fire1.png")
    emitter.behavior.image.scale = .5

    mscene = pyggel.scene.Scene()
    mscene.add_3d(img)
    mscene.add_3d(img2)
    mscene.add_3d(box)
    mscene.add_3d(sphere)
    mscene.add_3d_blend(img3)
    mscene.add_3d_blend(img5)
    mscene.add_3d_always(img4)
    mscene.add_2d(text)
    mscene.add_2d(text2)
    mscene.add_2d(text3)
    mscene.add_3d_blend(emitter)

    skybox = pyggel.geometry.Skybox(image.Texture("data/skybox.png"))
    skyball = pyggel.geometry.Skyball(image.Texture("data/skyball.png"))
    mscene.add_skybox(skybox)

    mscene.add_light(light)

    quads = []
    for x in xrange(10):
        for z in xrange(10):
            quads.append(pyggel.geometry.Quad(5, (x*5.5,0,z*5.5),
                                              texture=image.Texture("data/tile_example.png"),
                                              facing="top"))

    mscene.add_3d(pyggel.misc.StaticObjectGroup(quads))

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
##        print clock.get_fps()

        for event in pyggel.get_events():
            if event.type == QUIT:
                pyggel.quit()
                return None

            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if camera == camera1:
                        camera = camera2
                    else:
                        camera = camera1

                if event.key == K_s:
                    if mscene.graph.skybox == skybox:
                        mscene.graph.skybox = skyball
                    elif mscene.graph.skybox == skyball:
                        mscene.graph.skybox = None
                    else:
                        mscene.graph.skybox = skybox

                if event.key == K_SPACE:
                    misc.save_screenshot("test.png")

        key = pygame.key.get_pressed()
        if key[K_m]:
            if key[K_LEFT]:
                camera.posx -= .1
            if key[K_RIGHT]:
                camera.posx += .1
            if key[K_UP]:
                camera.posy -= .1
            if key[K_DOWN]:
                camera.posy += .1
            if key[K_MINUS]:
                camera.posz -= .1
            if key[K_EQUALS]:
                camera.posz += .1
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

        box.rotation[1] += 1

        pyggel.view.clear_screen(mscene)
        mscene.render(camera)
        pyggel.view.refresh_screen()

main()
