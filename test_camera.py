import pyggel
from pyggel import *

def main():
    pyggel.init(icon_image="data/ar.png")

    light = pyggel.light.Light((0,0,-5), (0,0,0,0),
                                  (1,1,1,1), (1,1,1,1),
                                  (0,0,0), True)

    camera1 = pyggel.camera.LookFromCamera((0,0,-10))
    camera2 = pyggel.camera.LookAtCamera((0,0,5), distance=10)

    font = pyggel.font.Font3D(None, 32)
    font2d = pyggel.font.Font(None, 32)
    img = font.make_text_image("Hello\nWorld: 3D", (1, 1, 0, 1))
    img.scale = 5
    img2 = font.make_text_image("Hello World: 3D X2!!!", (0, 1, 1, 1))
    img2.pos = (0, .7, 0)
    img3 = img2.copy()
    img3.pos = (0, 0, 0)
    img4 = font.make_text_image("Testy...123...", (0, 1, 0, 1))
    img4.pos = (0, -1, 0)
    img5 = img4.copy()

    del img5
    img5 = img4.copy()
    img5.colorize = (1, 0, 0, .5)
    img5.pos = (0, .1, 0)

    text = font2d.make_text_image("ARG!!!!", (1, 0, 0, 1))
    text2 = text.copy()
    text2.pos = (0,75)

    font2 = pyggel.font.MEFont(None, 32)
    text3 = font2.make_text_image("Testing -\n1, 2, 3", (0, 0, 1, 1))

    box = pyggel.geometry.Cube(5, texture=data.Texture("data/ar.png"))
    box.pos = (0,0,5)
    box.rotation = list(box.rotation)
    sphere = pyggel.geometry.Sphere(5, texture=data.Texture("data/ar.png"),
                                    show_inside=True)
    sphere.pos = (10, 0, 0)

    emitter = particle.Emitter3D(particle.Fire3D, (0, 0, -2))
    emitter.behavior.image = image.Image3D("data/fire1.png")
    emitter.behavior.image.scale = .5

    emitter2 = particle.EmitterPoint(particle.FirePoint, (2, 0, -2))

    mscene = pyggel.scene.Scene()
    mscene.camera = camera1
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
    mscene.add_3d(emitter2)

    skybox = pyggel.geometry.Skybox(data.Texture("data/skybox.png"))
    skyball = pyggel.geometry.Skyball(data.Texture("data/skyball.png"))
    mscene.add_skybox(skybox)

    mscene.add_light(light)

    quad = pyggel.geometry.Plane(50, (0,5,0),
                                 texture=data.Texture("data/tile_example.png"),
                                 tile=10)
    quad.rotation=(90,0,0)
    mscene.add_3d(quad)

    eh = pyggel.event.Handler()

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())

        eh.update()

        if eh.quit:
            pyggel.quit()
            return None
        if K_RETURN in eh.keyboard.hit:
            if mscene.camera == camera1:
                mscene.camera = camera2
            else:
                mscene.camera = camera1

        if "s" in eh.keyboard.hit:
            if mscene.graph.skybox == skybox:
                mscene.graph.skybox = skyball
            elif mscene.graph.skybox == skyball:
                mscene.graph.skybox = None
            else:
                mscene.graph.skybox = skybox

        if " " in eh.keyboard.hit:
            misc.save_screenshot("test.png")

        if "m" in eh.keyboard.active:
            if K_LEFT in eh.keyboard.active:
                mscene.camera.posx -= .1
            if K_RIGHT in eh.keyboard.active:
                mscene.camera.posx += .1
            if K_DOWN in eh.keyboard.active:
                mscene.camera.posy -= .1
            if K_UP in eh.keyboard.active:
                mscene.camera.posy += .1
            if "-" in eh.keyboard.active:
                mscene.camera.posz -= .1
            if "=" in eh.keyboard.active:
                mscene.camera.posz += .1
        if "r" in eh.keyboard.active:
            if K_LEFT in eh.keyboard.active:
                mscene.camera.roty -= .5
            if K_RIGHT in eh.keyboard.active:
                mscene.camera.roty += .5
            if K_DOWN in eh.keyboard.active:
                mscene.camera.rotx += .5
            if K_UP in eh.keyboard.active:
                mscene.camera.rotx -= .5
            if "-" in eh.keyboard.active:
                mscene.camera.rotz -= .5
            if "=" in eh.keyboard.active:
                mscene.camera.rotz += .5

        box.rotation[1] += 1

        pyggel.view.clear_screen(mscene)
        mscene.render()
        pyggel.view.refresh_screen()

main()
