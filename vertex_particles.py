import pyggel
from pyggel import *

def main():
    pyggel.init()

    my_light = light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)

    emitter = particle.EmitterPoint(particle.FirePoint)

    scene = pyggel.scene.Scene()
    scene.add_3d(emitter)

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pyggel.quit()
                return None

        view.clear_screen()
        scene.render(camera)
        view.refresh_screen()

main()
