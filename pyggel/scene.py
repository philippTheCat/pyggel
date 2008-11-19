from include import *
import camera, view

class Tree(object):
    def __init__(self):
        self.render_3d = []
        self.render_3d_blend = []
        self.render_2d = []
        self.render_3d_always = []

class Scene(object):
    def __init__(self):
        self.graph = Tree()

        self.render2d = True
        self.render3d = True

    def render(self, camera):
        if self.render3d:
            view.set3d()
            camera.push()
            for i in self.graph.render_3d: i.render(camera)
            for i in self.graph.render_3d_blend: i.render(camera)
            camera.pop()

        if self.render2d:
            view.set2d()
            for i in self.graph.render_2d: i.render()

    def add_2d(self, ele):
        self.graph.render_2d.append(ele)

    def test_textured(self, ele):
        if hasattr(ele, "textured") and ele.textured:
            return True
        return False

    def add_3d(self, ele):
        self.graph.render_3d.append(ele)

    def add_3d_blend(self, ele):
        self.graph.render_3d_blend.append(ele)

    def add_3d_always(self, ele):
        self.graph.render_3d_always.append(ele)
