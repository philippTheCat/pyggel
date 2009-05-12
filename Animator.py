import pyggel
from pyggel import *

import os

class ObjGroup(object):
    def __init__(self, name):
        self.name = name
        self.faces = []
        self.material = None

        self.visible = True
        self.dlist = None
        self.pickable = True

        self.pos = (0,0,0)
        self.rotation = (0,0,0)

        self.size = 0

    def compile(self, vertices, normals, texcoords, scale_factor):
        faces = []
        for face in self.faces:
            v,n,t = face
            uv, un, ut = [], [], []
            for i in xrange(len(v)):
                if n[i] > 0:
                    un.append(normals[n[i]-1])
                else:
                    un.append(None)

                if t[i] > 0:
                    ut.append(texcoords[t[i]-1])
                else:
                    ut.append(None)
                uv.append(vertices[v[i]-1])
            faces.append((uv, un, ut))

        x = y = z = 0
        num = 0
        for face in faces:
            v,n,t = face
            for i in v:
                x += i[0]
                y += i[1]
                z += i[2]
                num += 1
        px = x / num if (x and num) else 0
        py = y / num if (y and num) else 0
        pz = z / num if (z and num) else 0

        self.pos = (px,py,pz)

        final = []
        for face in faces:
            v,n,t = face
            nv = []
            for i in v:
                a,b,c = i
                a -= px
                b -= py
                c -= pz
                if a > 0: a += scale_factor
                else: a -= scale_factor
                if b > 0: b += scale_factor
                else: b -= scale_factor
                if c > 0: c += scale_factor
                else: c -= scale_factor
                nv.append((a,b,c))
            final.append((nv,n,t))

        #now build our display list!
        self.dlist = pyggel.data.DisplayList()
        self.dlist.begin()

        for face in final:
            v, n, t = face
            glBegin(GL_POLYGON)
            for i in xrange(len(v)):
                if n[i]:
                    glNormal3fv(n[i])
                if t[i]:
                    glTexCoord2fv(t[i])
                glVertex3fv(v[i])
            glEnd()

        self.dlist.end()

    def render(self, camera=None):
        glColor4f(*self.material.color)
        self.material.texture.bind()
        glPushMatrix()

        x,y,z = self.pos
        glTranslatef(x,y,z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)

        self.dlist.render()
        glPopMatrix()

class Material(object):
    def __init__(self, name):
        self.name = name
        self.color = (1,1,1,1)
        self.texture = pyggel.data.blank_texture

    def set_color(self, color):
        if len(color) == 3:
            color += (1,)
        self.color = color

def load_OBJ_for_manipulation(filename, scale_factor=0):
    view.require_init()

    objs = []
    mtls = {}

    vertices = []
    normals = []
    texcoords = []

    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == "o":
            objs.append(ObjGroup(values[1]))
        elif values[0] == 'v':
            vertices.append(map(float, values[1:4]))
        elif values[0] == 'vn':
            normals.append(map(float, values[1:4]))
        elif values[0] == 'vt':
            texcoords.append(map(float, values[1:3]))
        elif values[0] in ('usemtl', 'usemat'):
            objs[-1].material = mtls[values[1]]
        elif values[0] == 'mtllib':
            path = os.path.split(filename)[0]
            cur_mtl = None
            for line in open(os.path.join(path, values[1]), "r"):
                if line.startswith('#'): continue
                values = line.split()
                if not values: continue
                if values[0] == 'newmtl':
                    cur_mtl = Material(values[1])
                    mtls[cur_mtl.name] = cur_mtl
                elif cur_mtl is None:
                    raise ValueError, "mtl file doesn't start with newmtl stmt"
                elif values[0] == 'map_Kd':
                    cur_mtl.texture = data.Texture(os.path.join(path, values[1]))
                elif values[0]=="Kd":
                    cur_mtl.set_color(map(float, values[1:]))
        elif values[0] == 'f':
            face = []
            texcoords = []
            norms = []
            for v in values[1:]:
                w = v.split('/')
                face.append(int(w[0]))
                if len(w) >= 2 and len(w[1]) > 0:
                    texcoords.append(int(w[1]))
                else:
                    texcoords.append(0)
                if len(w) >= 3 and len(w[2]) > 0:
                    norms.append(int(w[2]))
                else:
                    norms.append(0)
            objs[-1].faces.append((face, norms, texcoords))

    for i in objs:
        i.compile(vertices, normals, texcoords, scale_factor)

    return objs

def main():
    pyggel.init()

    meh = pyggel.event.Handler()
    scene = pyggel.scene.Scene()
    scene.pick = True

    camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)
    my_light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)
    scene.add_light(my_light)

    regulars = load_OBJ_for_manipulation("data/bird_plane.obj")
    highlights = load_OBJ_for_manipulation("data/bird_plane.obj", .2)
    mapping = {}
    for i in zip(regulars, highlights):
        reg, hig = i
        hig.material.color = (.5,.5,.5,.5)
##        hig.scale = 1.2
        hig.visible = False
        hig.pickable = False
        mapping[reg] = hig
    scene.add_3d(regulars)
    scene.add_3d_blend(highlights)

##    pick_sphere = pyggel.geometry.Sphere(1, colorize=(.5,.5,.5,.5))
##    pick_sphere.visible = False
##    pick_sphere.pickable = False
##    scene.add_3d_blend(pick_sphere)

    while 1:
        meh.update()
        if meh.quit:
            pyggel.quit()
            return

        if K_LEFT in meh.keyboard.active:
            camera.roty -= .5
        if K_RIGHT in meh.keyboard.active:
            camera.roty += .5
        if K_DOWN in meh.keyboard.active:
            camera.rotx -= .5
        if K_UP in meh.keyboard.active:
            camera.rotx += .5
        if K_1 in meh.keyboard.active:
            camera.rotz -= .5
        if "2" in meh.keyboard.active: #just to throw you off ;)
            camera.rotz += .5

        if "=" in meh.keyboard.active:
            camera.distance -= .1
        if "-" in meh.keyboard.active:
            camera.distance += .1

        if "a" in meh.keyboard.active:
            camera.posx -= .1
        if K_d in meh.keyboard.active:
            camera.posx += .1
        if K_s in meh.keyboard.active:
            camera.posz -= .1
        if K_w in meh.keyboard.active:
            camera.posz += .1

        pyggel.view.clear_screen()

        cur_obj = scene.render(camera)
        if cur_obj:
##            pick_sphere.visible = True
##            x,y,z = cur_obj.pos
##            pick_sphere.pos = x,y,-z
##            pick_sphere.scale = cur_obj.size
            for i in mapping.values():
                i.visible = False
            mapping[cur_obj].visible = True
        else:
            for i in mapping.values():
                i.visible = False

        pyggel.view.refresh_screen()

main()
