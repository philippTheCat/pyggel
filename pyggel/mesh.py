"""
pyggle.mesh
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The mesh module contains mesh classes for different kinds of meshes, as well as loaders for various kinds of meshes.
"""

from include import *
import os
import image, view, data, misc, math3d
from scene import BaseSceneObject
import time
import random
import math

def OBJ(filename, pos=(0,0,0), rotation=(0,0,0), colorize=(1,1,1,1)):
    """Load a WaveFront OBJ mesh.
       filename must be the filename of the mesh to load
       pos/rotation/colorize are the starting attributes of the mesh object."""
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
    """Class to keep track of an objects verts and such while being loaded."""
    def __init__(self, name):
        """name is the name of the object."""
        self.name = name
        self.faces = []
        self.material = None

        self.dlist = None

    def compile(self, vertices, normals, texcoords):
        """Compile the ObjGroup into a CompiledGroup for rendering/using.
           vertices/normals/texcoords are a list of all attributes in the mesh file, fo reference"""
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

        avgx, avgy, avgz = 0,0,0

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
                avgx += x
                avgy += y
                avgz += z
                minx = min((minx, x))
                maxx = max((maxx, x))
                miny = min((miny, y))
                maxy = max((maxy, y))
                minz = min((minz, z))
                maxz = max((maxz, z))
            glEnd()

        avgx = math3d.safe_div(float(avgx), len(final))
        avgy = math3d.safe_div(float(avgy), len(final))
        avgz = math3d.safe_div(float(avgz), len(final))

        dlist.end()

        return CompiledGroup(self.name, self.material, dlist, (minx,miny,minz, maxx, maxy, maxz),
                             (avgx, avgy, avgz))

class CompiledGroup(BaseSceneObject):
    """The core object in a mesh, each mesh object (head, torso, w/e) has one of these.
       It has it's own attributes for pos/rotation/etc. and also is affected by the parent mesh's."""
    def __init__(self, name, material, dlist, dimensions, pos):
        """Create the Group
           name is the name of the object
           material is the data.Material object the group uses
           dlist is the display list of the object
           dimensions/pos are the size/center of the vertices in the object."""
        BaseSceneObject.__init__(self)
        self.name = name
        self.material = material
        self.display_list = dlist
        self.dimensions = dimensions

        self.base_pos = pos

    def get_dimensions(self):
        """Return the dimensions of the object."""
        d = self.dimensions
        return abs(d[0]-d[3]), abs(d[1]-d[4]), abs(d[2]-d[5])

    def render(self, camera=None):
        """Render the object.
           camera must be None of the camera object the scene is using to render."""
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
        """Return a copy of the object."""
        new = CompiledGroup(str(self.name),
                             self.material.copy(),
                             self.display_list,
                             self.dimensions,
                            self.base_pos)
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
    """Core mesh class, contains several objects representing the objects in the mesh."""
    def __init__(self, objs, pos=(0,0,0), rotation=(0,0,0),
                 scale=1, colorize=(1,1,1,1)):
        """Create the mesh object
           objs must be a lit of the CompiledGroup objects of the mesh
           pos/rotation/scale/colorize attributes of the mesh"""
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

    def get_names(self):
        """Return the names of all the objects in the mesh."""
        return [i.name for i in self.objs]

    def get_obj_by_name(self, name):
        """Return the CompiledGroup object reprensting the object <name>"""
        for i in self.objs:
            if i.name == name:
                return i
        return None

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


class Exploder(BaseSceneObject):
    """A simple class to explode/dismember a mesh object."""
    def __init__(self, root_mesh, speed=0.025, frame_duration=10):
        """Create the exploder
           root_mesh must be a BasicMesh object to explode
           speed is how fast you want each piece to move/rotate
           frame_duration is how many times it will update before dying"""
        BaseSceneObject.__init__(self)

        self.root_mesh = root_mesh
        self.angles = {}
        self.rots = {}
        for i in self.root_mesh.get_names():
            a = math3d.Vector(self.root_mesh.get_obj_by_name(i).base_pos)
            x, y, z = a.x, a.y, a.z
            if x == y == z == 0:
                x, y, z = misc.randfloat(-1,1), misc.randfloat(-1,1), misc.randfloat(-1,1)
            else:
                a = a.normalize()
                x, y, z = a.x, a.y, a.z

            y += misc.randfloat(1.5,2.5)
            self.angles[i] = x+misc.randfloat(-1,1), y+misc.randfloat(-1,1), z+misc.randfloat(-1,1)
            self.rots[i] = (misc.randfloat(-10, 10),
                            misc.randfloat(-10, 10),
                            misc.randfloat(-10, 10))

        self.speed = speed
        self.age = 0
        self.frame_duration = frame_duration

    def render(self, camera=None):
        """Update and render the explosion
           camera must be None or the camera the scene is using."""
        for i in self.root_mesh.objs:
            a, b, c = i.pos
            d,e,f = self.angles[i.name]
            a += d *self.speed
            b += e *self.speed
            c += f *self.speed
            i.pos = a, b, c
            e -= .015
            self.angles[i.name] = d,e,f
            a,b,c = i.rotation
            d,e,f = self.rots[i.name]
            a += d *self.speed*2
            b += e *self.speed*2
            c += f *self.speed*2
            i.rotation = (a,b,c)
        self.root_mesh.render(camera)

        self.age += 1
        if self.age >= self.frame_duration:
            self.dead_remove_from_scene = True

class FramedAnimationCommand(object):
    """A command for a FramedAnimation object."""
    def __init__(self, frames=1, commands=[],
                 frame_duration=1):
        """Create the command
            frames are the number of frames in the animation
            commands are a list of commands, specified like this:
                commands = [{obj_name:[(pos), (rotation), (scale)]}]
                Where each item in commands is what each named object does that frame, ie
                mesh[obj_name].pos = commands[frame][obj_name][0]
            frame_duration is how many updates each frame lasts"""

        self.frames = frames
        self.commands = commands

        self.cur_frame = 0
        self.frame_start_time = time.time()
        self.frame_duration = frame_duration

    def update(self):
        """Update the the animation, switching to the correct current frame."""
        if time.time() - self.frame_start_time >= self.frame_duration:
            self.frame_start_time = time.time()
            self.cur_frame += 1
            if self.cur_frame >= self.frames:
                self.cur_frame = 0

    def get_change(self, obj_name=None):
        """Return what obj_name should be doing in the current frame."""
        if not obj_name in self.commands[self.cur_frame]:
            return (0,0,0), (0,0,0), (1,1,1) #pos, rot, scale

        return self.commands[self.cur_frame][obj_name]

class ChildTree(object):
    def __init__(self):
        self.tree = {}
        self.all_objs = []
        self.root = None

    def add_object(self, obj, parent=None):
        if not self.tree:
            self.root = parent
        if parent in self.tree:
            self.tree[parent].append(obj)
        else:
            self.tree[parent] = [obj]
        self.all_objs.append(obj)

    def get_parents(self, obj):
        parents = []
        cur = obj
        while not cur == self.root:
            for i in self.tree:
                if cur in self.tree[i]: #found parent!
                    parents.append(i)
                    cur = i
                    break

        parents.reverse()
        return parents

class FramedAnimation(BaseSceneObject):
    def __init__(self, root_mesh, child_tree, commands={}):
        BaseSceneObject.__init__(self)

        self.root_mesh = root_mesh
        self.child_tree = child_tree
        self.commands = commands

        self.pos = root_mesh.pos
        self.rotation = root_mesh.rotation
        self.scale = root_mesh.scale
        self.colorize = root_mesh.colorize

        self.action = None

    def copy(self):
        new = FramedAnimation(self.root_mesh, self.child_tree, self.commands)
        new.pos = self.pos
        new.rotation = self.rotation
        new.scale = self.scale
        new.colorize = self.colorize
        new.action = self.action
        return new

    def get_obj_by_name(self, name):
        for i in self.root_mesh.objs:
            if i.name == name:
                return i
        return None

    def render(self, camera=None):
        use_ani = False
        if self.action:
            try:
                self.commands[self.action].update()
                use_ani = True
            except:
                print "action:", self.action, "does not exist!"

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

        if not use_ani:
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

        else:
            command = self.commands[self.action]

            #TODO: add outlining to active models?

            for i in self.child_tree.all_objs:
                glPushMatrix()
                obj = self.get_obj_by_name(i)
                for x in self.child_tree.get_parents(i):
                    pos, rot, sca = command.get_change(x)
                    glTranslatef(pos[0], pos[1], -pos[2])
                    a, b, c = rot
                    glRotatef(a, 1, 0, 0)
                    glRotatef(b, 0, 1, 0)
                    glRotatef(c, 0, 0, 1)
                    try:
                        glScalef(*sca)
                    except:
                        glScalef(sca,sca,sca)

                pos, rot, sca = command.get_change(i)
                glTranslatef(pos[0], pos[1], -pos[2])
                a, b, c = rot
                glRotatef(a, 1, 0, 0)
                glRotatef(b, 0, 1, 0)
                glRotatef(c, 0, 0, 1)
                try:
                    glScalef(*sca)
                except:
                    glScalef(sca,sca,sca)


                old = tuple(obj.material.color)
                r,g,b,a = old
                r2,g2,b2,a2 = self.colorize
                r *= r2
                g *= g2
                b *= b2
                a = a2
                obj.material.color = r,g,b,a
                obj.render(camera)
                obj.material.color = old
                glPopMatrix()
            glPopMatrix()


class InterpAnimationCommand(object):
    def __init__(self, commands=[], duration=1): #duration=seconds

        self.commands = commands
        self.duration = duration

        self.reset()

    def reset(self):
        self.time_stamp = time.time()

    def merge(self, a, b, amount=1):
        new = []
        for i in xrange(len(a)):
            new.append(a[i]+(b[i]*amount))
        return new

    def get_change(self, obj_name=None):
        age = time.time() - self.time_stamp
        if age >= self.duration:
            self.reset()
            age = 0

        pos = [0,0,0]
        rot = [0,0,0]
        sca = [1,1,1]
        for command in self.commands:
            if command[0] == obj_name:
                if command[5] <= age: #just apply fully!
                    pos = self.merge(pos, command[1])
                    rot = self.merge(rot, command[2])
                    sca = self.merge(sca, command[3])
                elif command[4] <= age <= command[5]: #now we have to figure out how much to merge!
                    mult = math3d.safe_div(float(age-command[4]), (command[5]-command[4]))
                    pos = self.merge(pos, command[1], mult)
                    rot = self.merge(rot, command[2], mult)
                    sca = self.merge(sca, command[3], mult)

        return pos, rot, sca

class InterpAnimation(FramedAnimation):
    def __init__(self, root_mesh, child_tree, commands={}):
        FramedAnimation.__init__(self, root_mesh, child_tree, commands)

    def copy(self):
        new = InterpAnimation(self.root_mesh, self.child_tree, self.commands)
        new.pos = self.pos
        new.rotation = self.rotation
        new.scale = self.scale
        new.colorize = self.colorize
        new.action = self.action
        return new

    def get_obj_by_name(self, name):
        for i in self.root_mesh.objs:
            if i.name == name:
                return i
        return None

    def render(self, camera=None):
        use_ani = False
        if self.action:
            try:
                self.commands[self.action]
##                self.commands[self.action].update()
                use_ani = True
            except:
                print "action:", self.action, "does not exist!"

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

        if not use_ani:
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

        else:
            command = self.commands[self.action]

            #TODO: add outlining to active models?

            for i in self.child_tree.all_objs:
                glPushMatrix()
                obj = self.get_obj_by_name(i)
                for x in self.child_tree.get_parents(i):
                    pos, rot, sca = command.get_change(x)
                    glTranslatef(pos[0], pos[1], -pos[2])
                    a, b, c = rot
                    glRotatef(a, 1, 0, 0)
                    glRotatef(b, 0, 1, 0)
                    glRotatef(c, 0, 0, 1)
                    try:
                        glScalef(*sca)
                    except:
                        glScalef(sca,sca,sca)

                pos, rot, sca = command.get_change(i)
                glTranslatef(pos[0], pos[1], -pos[2])
                a, b, c = rot
                glRotatef(a, 1, 0, 0)
                glRotatef(b, 0, 1, 0)
                glRotatef(c, 0, 0, 1)
                try:
                    glScalef(*sca)
                except:
                    glScalef(sca,sca,sca)


                old = tuple(obj.material.color)
                r,g,b,a = old
                r2,g2,b2,a2 = self.colorize
                r *= r2
                g *= g2
                b *= b2
                a = a2
                obj.material.color = r,g,b,a
                obj.render(camera)
                obj.material.color = old
                glPopMatrix()
            glPopMatrix()
        
