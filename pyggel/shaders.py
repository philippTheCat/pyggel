"""
pyggle.shaders
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The scene module contains classes used to represent an entire group of renderable objects.
"""

from include import *

try:
    from OpenGL.GL.ARB.shader_objects import *
    from OpenGL.GL.ARB.vertex_shader import *
    from OpenGL.GL.ARB.fragment_shader import *
    usable = True
except:
    usable = False

class Shader(object):
    def __init__(self, vertex_programs=[""], fragment_programs=[""]):
        if not usable:
            raise AttributeError("Shaders are not supported by either your system or your version of PyOpenGL!")

        self.program = glCreateProgramObjectARB()
        if type(vertex_programs) is type(""):
            vertex_programs = [vertex_programs]
        if type(fragment_programs) is type(""):
            fragment_programs = [fragment_programs]

        if vertex_programs:
            for i in vertex_programs:
                vertex_shader = glCreateShader(GL_VERTEX_SHADER)
                glShaderSourceARB(vertex_shader, [i])
                glCompileShaderARB(vertex_shader)
                glAttachObjectARB(self.program, vertex_shader)
                glDeleteObjectARB(vertex_shader)

        if fragment_programs:
            for i in fragment_programs:
                fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
                glShaderSourceARB(fragment_shader, [i])
                glCompileShaderARB(fragment_shader)
                glAttachObjectARB(self.program, fragment_shader)
                glDeleteObjectARB(fragment_shader)

        glValidateProgramARB(self.program)

        glLinkProgram(self.program)

    def run(self):
        glUseProgram(self.program)

    def __del__(self):
        try:
            glDeleteProgram(self.program)
        except:
            pass #already everything is closed, eh?
