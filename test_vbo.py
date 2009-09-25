
import pyggel
from pyggel import *

import random

rf = pyggel.misc.randfloat

class ColorGen(object):
    def __init__(self):
        self.cur_green = 1
        self.cur_o_dev = 0
        self.dire = -0.05

    def get_next(self):
        self.cur_green += rf(0,1)*self.dire
        if self.cur_green <= 0.5:
            self.dire = abs(self.dire)
        elif self.cur_green >= 0.9:
            self.dire = -abs(self.dire)

        self.cur_o_dev += rf(0,0.5)*self.dire
        if self.cur_o_dev >= 0.2:
            self.cur_o_dev = 0.2
        elif self.cur_o_dev < 0:
            self.cur_o_dev = 0
        return self.cur_o_dev, self.cur_green, self.cur_o_dev, 1

def get_points(size=(100,100)):
    array = []
    for x in xrange(size[0]+1):
        array.append([])
        for y in xrange(size[1]+1):
            array[x].append((x*5, rf(0,2), -y*5))
            array[x].append(((x+1)*5, rf(0,2), -y*5))

    verts = []
    norms = []
    colors = []
    col_gen = ColorGen()
    for x in xrange(size[0]):
        for y in xrange(size[1]):
            n1 = pyggel.math3d.calcTriNormal(array[x][y],
                                             array[x+1][y],
                                             array[x+1][y+1])
            n2 = pyggel.math3d.calcTriNormal(array[x][y],
                                             array[x+1][y+1],
                                             array[x][y+1])
            verts.append(array[x][y])
            verts.append(array[x+1][y])
            verts.append(array[x+1][y+1])
            norms.extend([n1]*3)

            verts.append(array[x][y])
            verts.append(array[x+1][y+1])
            verts.append(array[x][y+1])
            norms.extend([n2]*3)

            colors.extend([col_gen.get_next()]*6)

            
            
    return verts, norms, colors

def main():
    pyggel.view.init()

    camera = pyggel.camera.LookAtCamera(rotation=(-15,0,0), distance=15)
    my_light = pyggel.light.Light((50,100,50), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    verts, norms, colors = get_points((130,130))
    how_many = len(verts)

##    vert_vbo = data.VBOArray(GL_TRIANGLES, len(verts), "static")
    vert_vbo = data.get_best_array_type(GL_TRIANGLES, len(verts), 5)
    if pyggel.VBO_AVAILABLE and isinstance(vert_vbo, pyggel.data.VBOArray):
        have_vbo = True
    else:
        have_vbo = False
    vert_vbo.reset_verts(verts)
    vert_vbo.reset_colors(colors)
    vert_vbo.reset_norms(norms)

    meh = pyggel.event.Handler()

    last_index = 0

    clock = pygame.time.Clock()

    while 1:
        clock.tick(999)
        if have_vbo:
            pyggel.view.set_title("FPS with %s verts (using VBO): "%how_many+str(clock.get_fps()))
        else:
            pyggel.view.set_title("FPS with %s verts (not using VBO): "%how_many+str(clock.get_fps()))
        meh.update()
        if meh.quit:
            pyggel.quit()
            return None

        if K_UP in meh.keyboard.active:
            camera.posz += 0.1
        if K_DOWN in meh.keyboard.active:
            camera.posz -= 0.1
        if K_LEFT in meh.keyboard.active:
            camera.posx -= 0.1
        if K_RIGHT in meh.keyboard.active:
            camera.posx += 0.1

        view.set3d()

        colors = [(1,0,0,1), (0,1,0,1),
                  (0,0,1,1), (1,1,0,1),
                  (1,0,1,1), (0,1,1,1),
                  (.5,.5,.5,1)]

        view.clear_screen()
        my_light.shine()
        camera.push()
        vert_vbo.render()
        camera.pop()
        view.refresh_screen()

main()
