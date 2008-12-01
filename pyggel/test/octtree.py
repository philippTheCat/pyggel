import math3d, misc

import time

#this class is far too slow to be usable!

class TestObj(object):
    def __init__(self, pos):
        self.pos = pos
        self.vol_stor = misc.VolumeStore(self)

    def get_pos(self):
        return self.pos

    def get_dimensions(self):
        return 1,1,1

class OctTree(object):
    def __init__(self, parent=None, pos=(0,0,0), size=64):
        self.parent = parent
        self.pos = pos
        self.size = size

        self.num_sub_leaves = 0

        self.elements = []
        self.objs = []

        self.box = math3d.AABox(pos, size)

        if size > 4:
            nsize = size / 2
            nsize2 = size / 4
            x, y, z = self.pos
            self.num_sub_leaves = 8
            self.leaves = [OctTree(self, (x-nsize2, y-nsize2, z-nsize2), nsize),
                           OctTree(self, (x-nsize2, y+nsize2, z-nsize2), nsize),
                           OctTree(self, (x+nsize2, y+nsize2, z-nsize2), nsize),
                           OctTree(self, (x+nsize2, y-nsize2, z-nsize2), nsize),
                           OctTree(self, (x-nsize2, y-nsize2, z+nsize2), nsize),
                           OctTree(self, (x-nsize2, y+nsize2, z+nsize2), nsize),
                           OctTree(self, (x+nsize2, y+nsize2, z+nsize2), nsize),
                           OctTree(self, (x+nsize2, y-nsize2, z+nsize2), nsize)]
        else:
            self.leaves = []

        if self.parent:
            self.parent.num_sub_leaves += self.num_sub_leaves

    def add_obj(self, obj):
        if self.box.collide(obj.vol_stor.box):
            self.objs.append(obj)
        else:
            if obj in self.objs:
                self.objs.remove(obj)
        for i in self.leaves:
            i.add_obj(obj)

    def get_leaves_holding(self, obj):
        a = []
        if obj in self.objs:
            a.append(self)
            for i in self.leaves:
                a.extend(i.get_leaves_holding(obj))
        return a

    def get_bottom_leaves_holding(self, obj):
        x = self.get_leaves_holding(obj)
        n = []
        for i in x:
            if i.leaves == []:
                n.append(i)
        return n

    def get_objects_in_leaves_holding(self, obj):
        x = self.get_leaves_holding(obj)
        n = []
        for i in x:
            n.extend(i.objs)
        return list(set(n))

    def get_objects_in_bottom_leaves_holding(self, obj):
        x = self.get_bottom_leaves_holding(obj)
        n = []
        for i in x:
            n.extend(i.objs)
        return list(set(n))

t = OctTree()
n = TestObj((0, 25, 0))
from random import randint as ri
c = []
for i in xrange(10):
    c.append(TestObj((ri(-32, 32), ri(-32, 32), ri(-32, 32))))
    t.add_obj(c[-1])
    print 1
t.add_obj(n)
print len(t.get_leaves_holding(n)), len(t.get_bottom_leaves_holding(n))
print t.get_objects_in_bottom_leaves_holding(n)
