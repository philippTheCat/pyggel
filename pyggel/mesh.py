"""
pyggle.mesh
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *
import os
import image, view, misc

def MTL(filename, path=''):
    contents = {}
    mtl = None
    for line in open(os.path.join(path,filename), "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'newmtl':
            contents[values[1]] = None
            mtl = values[1]
        elif mtl is None:
            raise ValueError, "mtl file doesn't start with newmtl stmt"
        elif values[0] == 'map_Kd':
            # load the texture referred to by this declaration
            tex = image.Texture(os.path.join(path,mtl['map_Kd']), 1)
            contents[mtl] = tex
        elif values[0]=="Kd":
            #create a color texture
            tex = misc.create_empty_texture((8, 8), map(float, values[1:]))
            contents[mtl] = tex
        else:
            pass
    return contents
 
def OBJ(filename, swapyz=True, pos=(0,0,0),
        rotation=(0,0,0), colorize=(1,1,1,1)):
    """Loads a Wavefront OBJ file. """
    svertices = []
    snormals = []
    stexcoords = []
    sfaces = []

    material = None
    for line in open(filename, "r"):
        if line.startswith('#'): continue
        values = line.split()
        if not values: continue
        if values[0] == 'v':
            v = map(float, values[1:4])
            if swapyz:
                v = v[0], v[2], v[1]
            svertices.append(v)
        elif values[0] == 'vn':
            v = map(float, values[1:4])
            if swapyz:
                v = v[0], v[2], v[1]
            snormals.append(v)
        elif values[0] == 'vt':
            stexcoords.append(map(float, values[1:3]))
        elif values[0] in ('usemtl', 'usemat'):
            material = values[1]
        elif values[0] == 'mtllib':
            smtl = MTL(values[1], os.path.split(filename)[0])
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
            sfaces.append((face, norms, texcoords, material))

    gl_list = glGenLists(1)
    glNewList(gl_list, GL_COMPILE)
    for face in sfaces:
        vertices, normals, texture_coords, material = face
        mtl = smtl[material]
        try:
            mtl.bind()
        except:
            blank_texture.bind()
        glBegin(GL_POLYGON)
        for i in xrange(len(vertices)):
            if normals[i] > 0:
                glNormal3fv(snormals[normals[i] - 1])
            if texture_coords[i] > 0:
                glTexCoord2fv(stexcoords[texture_coords[i] - 1])
            glVertex3fv(svertices[vertices[i] - 1])
        glEnd()
    glEndList()

    verts = []
    for i in sfaces:
        for x in i[0]:
            verts.append(svertices[x-1])

    return BasicMesh(gl_list, pos, rotation, verts, 1, colorize)


class BasicMesh(object):
    def __init__(self, gl_list, pos=(0,0,0),
                 rotation=(0,0,0), verts=[],
                 scale=1, colorize=(1,1,1,1)):
        self.gl_list = gl_list
        self.pos = pos
        self.rotation = rotation
        self.verts = verts
        self.scale = scale
        self.colorize = colorize

    def copy(self):
        return BasicMesh(self.gl_list, list(self.pos),
                         list(self.rotation), list(self.verts),
                         self.scale, list(self.colorize))

    def render(self, camera=None):
        glPushMatrix()
        x,y,z = self.pos
        glTranslatef(x,y,-z)
        rot = self.rotation
        glRotatef(rot[0], 1, 0, 0)
        glRotatef(rot[1], 0, 1, 0)
        glRotatef(rot[2], 0, 0, 1)
        glScalef(self.scale, self.scale, self.scale)
        glColor4f(*self.colorize)
        glCallList(self.gl_list)
        glPopMatrix()
