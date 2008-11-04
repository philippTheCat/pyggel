from include import *
import camera, view

#####This code is not as fast as a straight "for" loop, but will remain as it will be helpful for the quadtree later...
##class Node(object):
##    def __init__(self, parent, obj):
##        self.parent = parent
##        self.obj = obj
##        self.c1 = self.c2 = self.c3 = self.c4 = None
##        self.weight = 1
##
##    def render(self):
##        if self.obj:
##            self.obj.render()
##        if self.c1:
##            self.c1.render()
##        if self.c2:
##            self.c2.render()
##        if self.c3:
##            self.c3.render()
##        if self.c4:
##            self.c4.render()
##
##    def add(self, obj):
##        ac = [self.c1, self.c2, self.c3, self.c4]
##        p = self.c1
##        for i in xrange(4):
##            ai = ac[i]
##            if ai == None:
##                c = Node(self, obj)
##                ac[i] = c
##                self.c1, self.c2, self.c3, self.c4 = ac
##                self.add_weight()
##                return None
##            if ai.weight < p.weight:
##                p = ai
##
##        p.add(obj)
##
##    def add_weight(self):
##        self.weight += 1
##        if self.parent:
##            self.parent.add_weight()
##
##class Leaf(Node):
##    def __init__(self):
##        Node.__init__(self, None, None)

class Tree(object):
    def __init__(self):
        self.render_with_camera = [] # Leaf() #this is the only one that should have shadowing!
        self.render_facing_camera = [] # Leaf()
        self.render_2d = [] # Leaf()

class Scene(object):
    def __init__(self):
        self.graph = Tree()

        self.render2d = True
        self.render3d = True

    def render(self, camera):
        view.clear_screen()
        if self.render3d:
            view.set3d()
            camera.push()
            for i in self.graph.render_with_camera: i.render()
            camera.set_facing_matrix()
            for i in self.graph.render_facing_camera: i.render()
            camera.pop()

        if self.render2d:
            view.set2d()
            for i in self.graph.render_2d: i.render()

    def add_2d(self, ele):
        self.graph.render_2d.append(ele)

    def add_3d(self, ele):
        self.graph.render_with_camera.append(ele)

    def add_3d_facing(self, ele):
        self.graph.render_facing_camera.append(ele)
