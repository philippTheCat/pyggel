from include import *
import camera, view

class Tree(object):
    def __init__(self):
        self.render_3d_nontextured = []
        self.render_3d_textured = []
        self.render_2d = []

class Scene(object):
    def __init__(self):
        self.graph = Tree()

        self.render2d = True
        self.render3d = True

    def render(self, camera):
        if self.render3d:
            view.set3d()
            camera.push()
            for i in self.graph.render_3d_nontextured: i.render(camera)
            for i in self.graph.render_3d_textured: i.render(camera)
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
        if self.test_textured(ele):
            self.graph.render_3d_textured.append(ele)
        else:
            self.graph.render_3d_nontextured.append(ele)
