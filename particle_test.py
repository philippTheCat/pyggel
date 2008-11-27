import pyggel
from pyggel import *

def main():
    pyggel.init()

##    my_light = light.Light((0,100,0), (0.5,0.5,0.5,1),
##                                  (1,1,1,1), (50,50,50,10),
##                                  (0,0,0), True)
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

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
        print clock.get_fps()
        for event in pygame.event.get():
            if event.type == QUIT:
                pyggel.quit()
                return None

            if event.type == KEYDOWN and event.key == K_SPACE:
                emitter.visible = not emitter.visible
                emitter2.visible = not emitter2.visible

        view.clear_screen()
        scene.render(camera)
        view.refresh_screen()

main()
