"""
pyggle.scene
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

from include import *
import camera, view, picker

class Tree(object):
    def __init__(self):
        self.render_3d = []
        self.render_3d_blend = []
        self.render_2d = []
        self.render_3d_always = []
        self.skybox = None
        self.lights = []

        self.pick_3d = picker.Group()

class Scene(object):
    def __init__(self):
        self.graph = Tree()

        self.render2d = True
        self.render3d = True

    def render(self, camera):
        view.set3d()
        if self.graph.skybox:
            self.graph.skybox.render(camera)
        if self.render3d:
            camera.push()
            for i in self.graph.lights:
                i.shine()
            glEnable(GL_ALPHA_TEST)
            for i in self.graph.render_3d: i.render(camera)
            glDisable(GL_ALPHA_TEST)
            glDepthMask(GL_FALSE)
            for i in self.graph.render_3d_blend: i.render(camera)
            glDepthMask(GL_TRUE)
            glDisable(GL_DEPTH_TEST)
            for i in self.graph.render_3d_always: i.render(camera)
            glEnable(GL_DEPTH_TEST)
            camera.pop()

        if self.render2d:
            view.set2d()
            glDisable(GL_LIGHTING)
            for i in self.graph.render_2d: i.render()
            if view.screen.lighting:
                glEnable(GL_LIGHTING)

    def add_2d(self, ele):
        self.graph.render_2d.append(ele)

    def test_textured(self, ele):
        if hasattr(ele, "textured") and ele.textured:
            return True
        return False

    def add_3d(self, ele):
        self.graph.render_3d.append(ele)
        self.graph.pick_3d.add_obj(ele)

    def add_3d_blend(self, ele):
        self.graph.render_3d_blend.append(ele)

    def add_3d_always(self, ele):
        self.graph.render_3d_always.append(ele)

    def add_skybox(self, ele):
        self.graph.skybox = ele

    def clear(self):
        glClear(GL_DEPTH_BUFFER_BIT)
        if not self.skybox:
            glClear(GL_COLOR_BUFFER_BIT)

    def add_light(self, light):
        self.graph.lights.append(light)

    def pick(self, mouse_pos, camera):
        view.set3d()
        self.graph.pick_3d.pick(mouse_pos, camera)
