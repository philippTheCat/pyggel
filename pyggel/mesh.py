"""
pyggle.mesh
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The mesh module contains mesh classes for different kinds of meshes, as well as loaders for various kinds of meshes.
"""

from include import *
import os
import image, view, data, misc
from scene import BaseSceneObject

def OBJ(filename, pos=(0,0,0), rotation=(0,0,0), colorize=(1,1,1,1)):
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
                    cur_mtl = data.Material(values[1])
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

    fin = []
    for i in objs:
        fin.append(i.compile(vertices, normals, texcoords))

    return BasicMesh(fin, pos, rotation, 1, colorize)
 
class ObjGroup(object):
    def __init__(self, name):
        self.name = name
        self.faces = []
        self.material = None

        self.dlist = None

    def compile(self, vertices, normals, texcoords):
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

        final = []
        for face in faces:
            v,n,t = face
            nv = []
            for i in v:
                a,b,c = i
                nv.append((a,b,c))
            final.append((nv,n,t))

        #now build our display list!
        dlist = data.DisplayList()
        dlist.begin()

        minx = miny = minz = 0
        maxx = maxy = maxz = 0

        for face in final:
            v, n, t = face
            glBegin(GL_POLYGON)
            for i in xrange(len(v)):
                if n[i]:
                    glNormal3fv(n[i])
                if t[i]:
                    glTexCoord2fv(t[i])
                glVertex3fv(v[i])
                x, y, z = v[i]
                minx = min((minx, x))
                maxx = max((maxx, x))
                miny = min((miny, y))
                maxy = max((maxy, y))
                minz = min((minz, z))
                maxz = max((maxz, z))
            glEnd()

        dlist.end()

        return CompiledGroup(self.name, self.material, dlist, (minx,miny,minz, maxx, maxy, maxz))

class CompiledGroup(BaseSceneObject):
    def __init__(self, name, material, dlist, dimensions):
        BaseSceneObject.__init__(self)
        self.name = name
        self.material = material
        self.display_list = dlist
        self.dimensions = dimensions

    def get_dimensions(self):
        d = self.dimensions
        return abs(d[0]-d[3]), abs(d[1]-d[4]), abs(d[2]-d[5])

    def render(self, camera=None):
        glPushMatrix()

        x,y,z = self.pos
        glTranslatef(x,y,z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)

        if self.outline:
            misc.outline(self.dlist, self.outline_color, self.outline_size)
        glColor4f(*self.material.color)
        self.material.texture.bind()
        self.display_list.render()
        glPopMatrix()

    def copy(self):
        new = CompiledGroup(str(self.name),
                             self.material.copy(),
                             self.display_list,
                             self.dimensions)
        new.pos = self.pos
        new.rotation = self.rotation
        new.scale = self.scale

        new.visible = self.visible
        new.pickable = self.pickable

        new.outline = self.outline
        new.outline_size = self.outline_size
        new.outline_color = self.outline_color
        return new

class BasicMesh(BaseSceneObject):
    def __init__(self, objs, pos=(0,0,0), rotation=(0,0,0),
                 scale=1, colorize=(1,1,1,1)):
        BaseSceneObject.__init__(self)

        self.objs = objs
        self.pos = pos
        self.rotation = rotation
        self.scale = scale
        self.colorize = colorize

    def get_dimensions(self):
        """Return the width, height and depth of the mesh..."""
        minx = miny = minz = 0
        maxx = maxy = maxz = 0
        for i in self.objs:
            d = i.dimensions
            minx = min(minx, d[0])
            maxx = max(maxx, d[3])
            miny = min(minx, d[1])
            maxy = max(maxx, d[4])
            minz = min(minx, d[2])
            maxz = max(maxx, d[5])

        return abs(minx-maxx), abs(miny-maxy), abs(minz-maxz)

    def copy(self):
        """Return a copy of the mesh, sharing the same data.DisplayList"""
        new_objs = []
        for i in self.objs:
            new_objs.append(i.copy())
        new = BasicMesh(new_objs, self.pos, self.rotation, self.scale, self.colorize)
        return new

    def render(self, camera=None):
        """Render the mesh
           camera must be None of the camera the scene is using"""
        glPushMatrix()
        x,y,z = self.pos
        glTranslatef(x,y,-z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        try:
            glScalef(*self.scale)
        except:
            glScalef(self.scale, self.scale, self.scale)
        glColor(*self.colorize)

        if self.outline:
            new = []
            for i in self.objs:
                x = i.copy()
                x.material = data.Material("blank")
                x.material.set_color(self.outline_color)
                x.outline = False
                new.append(x)
            misc.outline(misc.OutlineGroup(new),
                         self.outline_color, self.outline_size)

        for i in self.objs:
            old = tuple(i.material.color)
            r,g,b,a = old
            r2,g2,b2,a2 = self.colorize
            r *= r2
            g *= g2
            b *= b2
            a = a2
            i.material.color = r,g,b,a
            i.render(camera)
            i.material.color = old
        glPopMatrix()
