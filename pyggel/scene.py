from include import *

class Node(object):
    def __init__(self, parent, obj):
        self.parent = parent
        self.obj = obj
        self.c1 = self.c2 = self.c3 = self.c4 = None
        self.weight = 1

    def render(self):
        if self.obj:
            self.obj.render()
        if self.c1:
            self.c1.render()
        if self.c2:
            self.c2.render()
        if self.c3:
            self.c3.render()
        if self.c4:
            self.c4.render()

    def add(self, obj):
        ac = [self.c1, self.c2, self.c3, self.c4]
        p = self.c1
        for i in xrange(4):
            ai = ac[i]
            if ai == None:
                c = Node(self, obj)
                ac[i] = c
                self.c1, self.c2, self.c3, self.c4 = ac
                self.add_weight()
                return None
            if ai.weight < p.weight:
                p = ai

        p.add(obj)

    def add_weight(self):
        self.weight += 1
        if self.parent:
            self.parent.add_weight()

class Leaf(Node):
    def __init__(self):
        Node.__init__(self, None, None)

class Tree(object):
    def __init__(self):
        self.render_with_camera = Leaf() #this is the only one that should have shadowing!
        self.render_facing_camera = Leaf()
        self.render_2d = Leaf()
