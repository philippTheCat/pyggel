import pyggel
from pyggel import *

def main():
    pyggel.init()

    pyggel.view.set_lighting(False)
    pyggel.view.set_background_color((1,1,1))

    camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)

    emitter = particle.Emitter3D(particle.Fire3D)
    emitter.behavior.image = image.Image3D("data/fire1.png")
    emitter.behavior.image.scale = .5

    emitter2 = particle.EmitterPoint(particle.FirePoint)
    emitter2.visible = False

    scene = pyggel.scene.Scene()
    scene.add_3d_blend(emitter)
    scene.add_3d_blend(emitter2)

    eh = event.Handler()

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())

        eh.update()
        if eh.quit:
            pyggel.quit()
            return None
        if " " in eh.keyboard.hit:
            emitter.visible = not emitter.visible
            emitter2.visible = not emitter2.visible

        view.clear_screen()
        scene.render(camera)
        view.refresh_screen()

main()
