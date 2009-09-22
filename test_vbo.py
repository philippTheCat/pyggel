
import pyggel
from pyggel import *

import random

def main():
    pyggel.view.init()
    pyggel.view.set_lighting(False)
    glDisable(GL_CULL_FACE)

    vbo = data.VBOArray(GL_QUADS, 4, "stream")
    vbo.reset_verts([(0,0,-5), (0,1,-5),
                      (1,1,-5), (1,0,-5)])
    vbo.reset_colors([(1,1,1,1),
                       (1,1,1,1),
                       (1,1,1,1),
                       (1,1,1,1)])

    emitter2 = particle.EmitterPoint(particle.FirePoint, pos=(0,0,-5))

    meh = pyggel.event.Handler()

    last_index = 0

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
        pyggel.view.set_title(str(clock.get_fps()))
        meh.update()
        if meh.quit:
            pyggel.quit()
            return None

        view.set3d()

        colors = [(1,0,0,1), (0,1,0,1),
                  (0,0,1,1), (1,1,0,1),
                  (1,0,1,1), (0,1,1,1),
                  (.5,.5,.5,1)]

        [vbo.update_colors(i, random.choice(colors)) for i in xrange(4)]

        cur_point = vbo.verts.data[0]
        vbo.update_verts(0, (cur_point[0]-0.001, 0, -5))

        view.clear_screen()
        vbo.render()
        emitter2.render()
        view.refresh_screen()

main()
