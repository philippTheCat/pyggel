import pyggel
from pyggel import *

import random, time

class Bone(object):
    def __init__(self, start, end, anchor=0):
        self._start = start
        self._end = end
        self._anchor = anchor

        self.cur_start = self._start
        self.cur_end = self._end

        self.children = []

        self.rotation = (0,0,0)
        self.movement = (0,0,0)
        self.scale = (1,1,1)

    def get_anchor(self):
        a,b,c = self.cur_end
        d,e,f = self.cur_start
        a2 = (a - d)*self._anchor + d
        b2 = (b - e)*self._anchor + e
        c2 = (c - f)*self._anchor + f
        return a2,b2,c2

    def copy(self):
        new = Bone(self._start, self._end, self._anchor)
        new.cur_start = self.cur_start
        new.cur_end = self.cur_end
        new.cur_anchor = self.cur_anchor

        for i in self.children:
            new.children.append(i.copy())

        new.rotation = self.rotation
        new.scale = self.scale
        return new

    def merge(self, a, b, amount=1):
        new = []
        for i in xrange(len(a)):
            new.append(a[i]+(b[i]*amount))
        return new

    def dif3(self, a, b, amount=1):
        dif = []
        for i in xrange(3):
            dif.append((a[i]-b[i])*amount)
        return dif

    def move(self, x,y,z):
        self.movement = self.merge(self.movement, (x,y,z))

    def rotate(self, x, y, z):
        self.rotation = self.merge(self.rotation, (x,y,z))

    def push_rotation(self, rot=None, anchor=None):
        if not anchor:
            anchor = self.get_anchor()
        if not rot:
            x,y,z = self.rotation
        else:
            x,y,z = rot

        vec1 = pyggel.math3d.Vector(anchor)
        vec2 = pyggel.math3d.Vector(self.cur_start)
        vec3 = pyggel.math3d.Vector(self.cur_end)

        new1 = vec2.rotate(vec1, (-x, y, z))
        new2 = vec3.rotate(vec1, (-x, y, z))

        self.cur_start = new1.get_pos()
        self.cur_end = new2.get_pos()

        for i in self.children:
            i.push_rotation((x,y,z), anchor)

    def push_move(self, pos=None):
        if not pos:
            pos = self.movement
        self.cur_start = self.merge(pos, self.cur_start)
        self.cur_end = self.merge(pos, self.cur_end)
        for i in self.children:
            i.push_move(pos)

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
        self.movement = (0,0,0)
        self.cur_start = self._start
        self.cur_end = self._end
        self.scale = (1,1,1)

    def push(self):
        self.push_rotation()
        self.push_move()

class CoreAnimationCommand(object):
    def __init__(self, obj, val, start, end):
        self.obj = obj
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
            obj.rotate(a,b,c)
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

        self.reset_when_done = True

        self.reset(None)

    def reset(self, skeleton):
        self.start()

    def start(self):
        self.tstamp_start = time.time()
        self.tstamp_last = time.time()
        self.finished_frame = False

    def update(self, skeleton):
        age = time.time() - self.tstamp_start
        if age >= self.duration:
            age = self.duration
        for i in self.commands:
            i.update(skeleton, self.tstamp_last-self.tstamp_start, age)
        self.tstamp_last = age
        if age == self.duration:
            if self.reset_when_done:
                self.reset()
            self.finished_frame = True

class Skeleton(object):
    def __init__(self):
        self.bones = {}

    def add_bone(self, name, start, end, parent=None, anchor=0):
        new = Bone(start, end, anchor)
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

    def reset(self):
        for i in self.bones:
            self.bones[i].reset()

    def push(self):
        for i in self.bones:
            self.bones[i].push()

class Animation(object):
    def __init__(self, mesh, skeleton, commands):
        self.mesh = mesh
        self.skeleton = skeleton
        self.commands = commands

        self.do()

        self.pos = (0,0,0)
        self.rotation = (0,0,0)
        self.scale = (1,1,1)
        self.colorize=(1,1,1,1)

    def do(self, action=None, loop=True, reset_when_done=True, reset_first=True):
        self.action = action
        self.loop = loop
        self.reset_when_done = reset_when_done

        if reset_first:
            self.skeleton.reset()

        if self.action in self.commands:
            self.commands[self.action].start()

    def render(self, camera=None):
        use_ani = False
        if self.action:
            if self.action in self.commands:
                if self.action in self.commands:
                    self.commands[self.action].reset_when_done = self.reset_when_done
                command = self.commands[self.action]
                command.update(self.skeleton)
                if command.finished_frame:
                    if not self.loop:
                        self.action = None

        self.skeleton.push()

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

        #TODO: add outlining to active models?

        for i in self.mesh.objs:
            _pos, _rot, _sca = i.pos, i.rotation, i.scale
            if i.name in self.skeleton.bones:
                bone = self.skeleton.bones[i.name]
                npos = bone.get_center()
                x, y, z = bone.rotation
                nrot = x, y, -z
                nsca = bone.scale

                i.pos = npos
                i.rotation = nrot
                i.scale = nsca

            old = tuple(i.material.color)
            r,g,b,a = old
            r2,g2,b2,a2 = self.colorize
            r *= r2
            g *= g2
            b *= b2
            a *= a2
            i.material.color = r,g,b,a
            i.render(camera)
            i.material.color = old

            i.pos, i.rotation, i.scale = _pos, _rot, _sca
        glPopMatrix()

        self.skeleton.reset()

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
    skel.add_bone(root.name, (0,0,root.side("back")), (0,0,root.side("front")))
    skel.add_bone(tail.name, (0,0,tail.side("front")), (0,0,tail.side("back")), root.name)
    skel.add_bone(head.name, (0,0,head.side("back")), (0,0,head.side("front")), root.name, 0.25)
    skel.add_bone(wings.name, (wings.side("left"),0,0), (wings.side("right"),0,0), root.name, 0.5)

    action = Action(2, [RotateTo(wings.name, (0,25,45),0,.5),
                        RotateTo(wings.name, (0,-25,-45),.5,1.5),
                        RotateTo(wings.name, (0,0,0),1.5,2),
                        ScaleTo(tail.name, (1.25,1.25,1.25), 0, 1),
                        ScaleTo(tail.name, (1,1,1), 1, 2),
                        RotateTo(head.name, (0,15,0),0,.25),
                        RotateTo(head.name, (0,-15,0),.25,.75),
                        RotateTo(head.name, (0,0,0),.75,1)])
    head_left = Action(1, [RotateTo(head.name, (0,45,0),0,1)])
    head_right = Action(1, [RotateTo(head.name, (0,-45,0), 0,1)])
    head_up = Action(1, [RotateTo(head.name, (45,0,0),0,1)])
    head_down = Action(1, [RotateTo(head.name, (-45,0,0),0,1)])
    head_test = Action(5, [RotateTo(head.name, (0,0,45),0,1),
                           RotateTo(head.name, (0,-45,0),2,3),
                           RotateTo(head.name, (0,0,0),4,5),
                           RotateTo(tail.name, (0,0,360), 0,5)])
    ani = Animation(obj, skel, {"1":head_left,
                                "2":head_right,
                                "3":head_up,
                                "4":head_down,
                                "5":action,
                                "6":head_test})

    #Let's make some connections here:
    new_obj = head.copy()
    new_obj.name = "weapon_right"
    skel.add_bone(new_obj.name, (wings.side("right"),0,0), (wings.side("right")+new_obj.side("width"),0,0), wings.name)
    ani.mesh.objs.append(new_obj)
    new_obj2 = head.copy()
    new_obj2.name = "weapon_left"
    skel.add_bone(new_obj2.name, (wings.side("left"),0,0), (wings.side("left")-new_obj2.side("width"),0,0), wings.name)
    ani.mesh.objs.append(new_obj2)

    #and connect a new item to each of those too!
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

    last = None

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

        nums = ("1", "2", "3", "4", "5", "6", "7")
        for i in nums:
            if i in meh.keyboard.hit:
                ani.do(i, False, False, False)
        if "r" in meh.keyboard.hit:
            ani.do(None, False, True, True)

        pyggel.view.clear_screen()

        pyggel.view.set3d()
        camera.push()

        ani.render()

        camera.pop()
        pyggel.view.refresh_screen()
main()
