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
        self.pick_3d_blend = picker.Group()
        self.pick_3d_always = picker.Group()

class PickResult(object):
    def __init__(self, hits, depths):
        self.hit3d, self.hit3d_blend, self.hit3d_always = hits
        self.dep3d, self.dep3d_blend, self.dep3d_always = depths

        a, b, c = depths
        if a == None: a = 100
        if b == None: b = 100
        if c == None: c = 100
        depths = [a, b, c]

        self.hit = hits[depths.index(min(depths))]

class RenderObject(object):
    def __init__(self):
        self.camera = None

    def render(self, obj):
        if obj.visible:
            obj.render(self.camera)

class Scene(object):
    def __init__(self):
        self.graph = Tree()

        self.render2d = True
        self.render3d = True

        self.rObj = RenderObject()

    def render(self, camera):
        self.rObj.camera = camera
        view.set3d()
        if self.graph.skybox:
            self.graph.skybox.render(camera)
        if self.render3d:
            camera.push()
            for i in self.graph.lights:
                i.shine()
            glEnable(GL_ALPHA_TEST)
            map(self.rObj.render, self.graph.render_3d)
            glDisable(GL_ALPHA_TEST)
            glDepthMask(GL_FALSE)
            map(self.rObj.render, self.graph.render_3d_blend)
            glDepthMask(GL_TRUE)
            glDisable(GL_DEPTH_TEST)
            map(self.rObj.render, self.graph.render_3d_always)
            glEnable(GL_DEPTH_TEST)
            camera.pop()

        if self.render2d:
            view.set2d()
            glDisable(GL_LIGHTING)
            map(self.rObj.render, self.graph.render_2d)
            if view.screen.lighting:
                glEnable(GL_LIGHTING)

    def add_2d(self, ele):
        self.graph.render_2d.append(ele)

    def remove_2d(self, ele):
        self.graph.render_2d.remove(ele)

    def add_3d(self, ele):
        self.graph.render_3d.append(ele)
        self.graph.pick_3d.add_obj(ele)

    def remove_3d(self, ele):
        self.graph.render_3d.remove(ele)
        self.graph.pick_3d.rem_obj(ele)

    def add_3d_blend(self, ele):
        self.graph.render_3d_blend.append(ele)
        self.graph.pick_3d_blend.add_obj(ele)

    def remove_3d_blend(self, ele):
        self.graph.render_3d_blend.remove(ele)
        self.graph.pick_3d_blend.rem_obj(ele)

    def add_3d_always(self, ele):
        self.graph.render_3d_always.append(ele)
        self.graph.pick_3d_always.add_obj(ele)

    def remove_3d_always(self, ele):
        self.graph.render_3d_always.remove(ele)
        self.graph.pick_3d_always.rem_obj(ele)

    def add_skybox(self, ele):
        self.graph.skybox = ele

    def add_light(self, light):
        self.graph.lights.append(light)

    def pick(self, mouse_pos, camera):
        view.set3d()

        glEnable(GL_ALPHA_TEST)
        h1 = self.graph.pick_3d.pick(mouse_pos, camera)
        glDisable(GL_ALPHA_TEST)

        glDepthMask(GL_FALSE)
        h2 = self.graph.pick_3d_blend.pick(mouse_pos, camera)
        glDepthMask(GL_TRUE)

        glDisable(GL_DEPTH_TEST)
        h3 = self.graph.pick_3d_always.pick(mouse_pos, camera)
        glEnable(GL_DEPTH_TEST)

        hits = []
        depths = []

        if h1:
            hits.append(h1[0])
            depths.append(h1[1])
        else:
            hits.append(None)
            depths.append(None)

        if h2:
            hits.append(h2[0])
            depths.append(h2[1])
        else:
            hits.append(None)
            depths.append(None)

        if h3:
            hits.append(h3[0])
            depths.append(h3[1])
        else:
            hits.append(None)
            depths.append(None)

        view.clear_screen()
        return PickResult(hits, depths)
