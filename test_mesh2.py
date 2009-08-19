import pyggel
from pyggel import *

import random, time

class Bone(object):
    def __init__(self, start, end):
        self._start = start
        self._end = end

        self.cur_start = self._start
        self.cur_end = self._end

        self.children = []

        self.rotation = (0,0,0)
        self.scale = (1,1,1)

    def copy(self):
        new = Bone(self._start, self._end)
        new.cur_start = self.cur_start
        new.cur_end = self.cur_end

        for i in self.children:
            new.children.append(i.copy())

        new.rotation = self.rotation
        new.scale = self.scale
        return new

    def merge(self, a, b):
        new = []
        for i in xrange(len(a)):
            new.append(a[i]+b[i])
        return new

    def dif3(self, a, b):
        dif = []
        for i in xrange(3):
            dif.append(a[i]-b[i])
        return dif

    def move(self, x,y,z):
        self.cur_start = self.merge(self.cur_start, (x,y,z))
        self.cur_end = self.merge(self.cur_end, (x,y,z))
        for i in self.children:
            i.move(x,y,z)

    def rotate(self, x, y, z, anchor=None):
        if not anchor:
            anchor = self.cur_start
        vec1 = pyggel.math3d.Vector(anchor)
        vec2 = pyggel.math3d.Vector(self.cur_start)
        vec3 = pyggel.math3d.Vector(self.cur_end)
        new1 = vec2.rotate(vec1, (-x, y, z))
        new2 = vec3.rotate(vec1, (-x, y, z))

        self.cur_start = new1.get_pos()
        self.cur_end = new2.get_pos()
        self.rotation = self.merge(self.rotation, (x,y,z))

        for i in self.children:
            i.rotate(x,y,z, anchor)

    def scaled(self, x,y,z):
        self.scale = self.merge(self.scale, (x,y,z))
        for i in self.children:
            i.scaled(x,y,z)

    def get_center(self):
        a,b,c = self.cur_start
        d,e,f = self.cur_end
        return (pyggel.math3d.safe_div(a+d, 2.0),
                pyggel.math3d.safe_div(b+e, 2.0),
                pyggel.math3d.safe_div(c+f, 2.0))

    def get_points(self):
        return self.cur_start, self.get_center(), self.cur_end

    def reset(self):
        self.rotation = (0,0,0)
        self.cur_start = self._start
        self.cur_end = self._end
        self.scale = (1,1,1)

class CoreAnimationCommand(object):
    def __init__(self, obj, val, start, end, anchor=None):
        self.obj = obj
        self.anchor = anchor
        self.val = val
        self.start = start
        self.end = end

    def _m(self, a, b, amount=1):
        new = []
        for i in xrange(len(a)):
            new.append(a[i]+(b[i]*amount))
        return new

    def _d(self, a, b, amount=1):
        new = []
        for i in xrange(len(a)):
            new.append((a[i]-b[i])*amount)
        return new

    def update(self, skeleton, tstamp_last, tstamp_cur):
        if self.obj in skeleton.bones:
            obj = skeleton.bones[self.obj]
        else:
            return None
        pos, rotation, scale = obj.get_center(), obj.rotation, obj.scale
        if tstamp_last > self.end or tstamp_cur < self.start:
            return None
        _s = max((tstamp_last, self.start))
        _e = min((tstamp_cur, self.end))
        mult = pyggel.math3d.safe_div(float(_e-_s), self.end-_s)
        if self.ident == "RT":
            a,b,c = self._d(self.val, rotation, mult)
            obj.rotate(a,b,c,self.anchor)
        if self.ident == "MT":
            pos = self._d(self.val, pos, mult)
            obj.move(*pos)
        if self.ident == "ST":
            scale = self._d(self.val, scale, mult)
            obj.scaled(*scale)

    def reset(self, skeleton):
        if self.obj in skeleton.bones:
            skeleton.bones[self.obj].reset()

class RotateTo(CoreAnimationCommand):
    ident = "RT"

class MoveTo(CoreAnimationCommand):
    ident = "MT"

class ScaleTo(CoreAnimationCommand):
    ident = "ST"

class Action(object):
    def __init__(self, duration, commands):
        self.duration = duration
        self.commands = commands

        self.reset(None)

    def reset(self, skeleton):
        self.tstamp_start = time.time()
        self.tstamp_last = time.time()
        if skeleton:
            for i in self.commands:
                i.reset(skeleton)

    def update(self, skeleton):
        age = time.time() - self.tstamp_start
        if age >= self.duration:
            age = self.duration
        for i in self.commands:
            i.update(skeleton, self.tstamp_last, age)
        self.tstamp_last = age
        if age == self.duration:
            self.reset(skeleton)

class Skeleton(object):
    def __init__(self):
        self.bones = {}

    def add_bone(self, name, start, end, parent=None):
        new = Bone(start, end)
        if parent:
            self.bones[parent].children.append(new)
        self.bones[name] = new
        return new

    def get(self, name):
        return self.bones[name]

    def copy(self):
        new = Skeleton()
        for i in self.bones:
            new[i] = self.bones[i].copy()
        return new

class Animation(object):
    def __init__(self, mesh, skeleton, commands):
        self.mesh = mesh
        self.skeleton = skeleton
        self.commands = commands

        self.action = None

        self.pos = (0,0,0)
        self.rotation = (0,0,0)
        self.scale = (1,1,1)
        self.colorize=(1,1,1,1)

    def render(self, camera=None):
        use_ani = False
        if self.action:
            try:
                self.commands[self.action]
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
            for i in self.mesh.objs:
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
            command.update(self.skeleton)

            #TODO: add outlining to active models?

            for i in self.mesh.objs:
                _pos, _rot, _sca = i.pos, i.rotation, i.scale
                if i.name in self.skeleton.bones:
                    bone = self.skeleton.bones[i.name]
                    npos = bone.get_center()
                    x, y, z = bone.rotation
                    z = -z
                    nrot = x, y, z
                    nsca = bone.scale

                    i.pos = npos
                    i.rotation = nrot
                    i.scale = nsca

                i.render(camera)

                i.pos, i.rotation, i.scale = _pos, _rot, _sca

def main():
    pyggel.view.init(screen_size=(800,600), screen_size_2d=(640, 480))
    pyggel.view.set_debug(False)

    my_light = pyggel.light.Light((0,100,0), (0.5,0.5,0.5,1),
                                  (1,1,1,1), (50,50,50,10),
                                  (0,0,0), True)

    camera = pyggel.camera.LookAtCamera((0,0,0), distance=10)
    camera.roty = 180

    obj = pyggel.mesh.OBJ("data/bird_plane.obj")
    root = obj.get_obj_by_name("cylinder1")
    tail = obj.get_obj_by_name("sphere2")
    head = obj.get_obj_by_name("sphere2_copy3")
    wings = obj.get_obj_by_name("cube4")

    skel = Skeleton()
    skel.add_bone(root.name, (0,0,root.side("back")), (0,0,root.dimensions[2]))
    skel.add_bone(tail.name, (0,0,tail.dimensions[5]), (0,0,tail.dimensions[2]), root.name)
    skel.add_bone(head.name, (0,0,head.dimensions[2]), (0,0,head.dimensions[5]), root.name)
    skel.add_bone(wings.name, (wings.dimensions[0],0,0), (wings.dimensions[3],0,0), root.name)

    action = Action(2, [RotateTo(wings.name, (0,0,45),0,.5,(0,0,0)),
                        RotateTo(wings.name, (0,0,-45),.5,1.5,(0,0,0)),
                        RotateTo(wings.name, (0,0,0),1.5,2,(0,0,0)),
                        ScaleTo(tail.name, (1.25,1.25,1.25), 0, 1),
                        ScaleTo(tail.name, (1,1,1), 1, 2),
                        RotateTo(head.name, (0,15,0),0,.25,(0,0,-.5)),
                        RotateTo(head.name, (0,-15,0),.25,.75,(0,0,-.5)),
                        RotateTo(head.name, (0,0,0),.75,1,(0,0,-.5)),

                        RotateTo("weapon_left", (0,0,90), 0, .5),
                        RotateTo("weapon_left", (0,0,-90), .5, 1.5),
                        RotateTo("weapon_left", (0,0,0), 1.5, 2),
                        RotateTo("weapon_right", (0,0,90), 0, .5),
                        RotateTo("weapon_right", (0,0,-90), .5, 1.5),
                        RotateTo("weapon_right", (0,0,0), 1.5, 2),

                        RotateTo("weapon_right_2", (0,0,90), 0, .5),
                        RotateTo("weapon_right_2", (0,0,-90), .5, 1.5),
                        RotateTo("weapon_right_2", (0,0,0), 1.5, 2),
                        RotateTo("weapon_left_2", (0,0,90), 0, .5),
                        RotateTo("weapon_left_2", (0,0,-90), .5, 1.5),
                        RotateTo("weapon_left_2", (0,0,0), 1.5, 2)])
    ani = Animation(obj, skel, {"move":action})
    ani.action = "move"

    #Let's make some connections here:
    new_obj = head.copy()
    new_obj.name = "weapon_right"
    skel.add_bone(new_obj.name, (wings.side("right"),0,0), (wings.side("right")+new_obj.side("width"),0,0), wings.name)
    ani.mesh.objs.append(new_obj)
    new_obj2 = head.copy()
    new_obj2.name = "weapon_left"
    skel.add_bone(new_obj2.name, (wings.side("left"),0,0), (wings.side("left")-new_obj2.side("width"),0,0), wings.name)
    ani.mesh.objs.append(new_obj2)

    #and connect a new item to eachof those too!
    new_obj3 = head.copy()
    new_obj3.name = "weapon_left_2"
    skel.add_bone(new_obj3.name,
                  (wings.side("left")-new_obj2.side("width"),0,0),
                  (wings.side("left")-new_obj2.side("width")*2,0,0), new_obj2.name)
    ani.mesh.objs.append(new_obj3)

    new_obj4 = head.copy()
    new_obj4.name = "weapon_right_2"
    skel.add_bone(new_obj4.name,
                  (wings.side("right")+new_obj.side("width"),0,0),
                  (wings.side("right")+new_obj.side("width")*2,0,0), new_obj.name)
    ani.mesh.objs.append(new_obj4)

    clock = pygame.time.Clock()

    meh = pyggel.event.Handler()
    meh.bind_to_event(" ", lambda a,b: pyggel.misc.save_screenshot("Test.png"))

    while 1:
        clock.tick(999)
        pyggel.view.set_title("FPS: %s"%clock.get_fps())

        meh.update()

        if meh.quit:
            pyggel.quit()
            return None

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

        pyggel.view.set3d()
        camera.push()

        ani.render()

        camera.pop()
        pyggel.view.refresh_screen()
main()
