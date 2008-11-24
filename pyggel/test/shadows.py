from include import *
from OpenGL.GL.ARB.shadow import *
from OpenGL.GL.ARB.depth_texture import *
from OpenGL.GL.ARB.transpose_matrix import *

class ShadowMap(object):
    def __init__(self):
        self.gl_tex = glGenTextures(1)
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 512, 512, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, None)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        self.sm2 = None

    def create_shadow_before(self, light):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1, .1, 100)
        LightProjectionMatrix = glGetFloatv(GL_PROJECTION_MATRIX)
        glMatrixMode(GL_MODELVIEW)

        glLoadIdentity()
        a, b, c = light.pos
        glTranslatef(-a, b, c)

        LightViewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

        glViewport(0,0,512,512)
        glPolygonOffset(0,1000)
        glEnable(GL_POLYGON_OFFSET_FILL)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadMatrixf([[.5, 0, 0, 0],
                       [0, .5, 0, 0],
                       [0, 0, .5, 0],
                       [.5, .5, .5, 1]])
        glMultMatrixf(LightProjectionMatrix)
        glMultMatrixf(LightViewMatrix)

        TextureMatrix = glGetFloatv(GL_TRANSPOSE_MODELVIEW_MATRIX)

        self.sm2 = TextureMatrix

    def create_shadow_after(self):
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)
        glCopyTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 0, 0, 512, 512)
        glDisable(GL_POLYGON_OFFSET_FILL)
        blank_texture.bind()

    def render_shadow_compare_before(self):
        glEnable(GL_TEXTURE_GEN_S)
        glEnable(GL_TEXTURE_GEN_T)
        glEnable(GL_TEXTURE_GEN_R)
        glEnable(GL_TEXTURE_GEN_Q)
        glBindTexture(GL_TEXTURE_2D, self.gl_tex)
        TextureMatrix = self.sm2
        glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
        glTexGenfv(GL_S, GL_EYE_PLANE, TextureMatrix[0])
        glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
        glTexGenfv(GL_T, GL_EYE_PLANE, TextureMatrix[1])
        glTexGeni(GL_R, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
        glTexGenfv(GL_R, GL_EYE_PLANE, TextureMatrix[2])
        glTexGeni(GL_Q, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
        glTexGenfv(GL_Q, GL_EYE_PLANE, TextureMatrix[3])
        #Enable shadow comparison
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE_ARB, GL_COMPARE_R_TO_TEXTURE_ARB)
        #Shadow comparison should be True (in shadow) if r > texture
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC_ARB, GL_GREATER)
        #Shadow comparison should generate an INTENSITY result
        glTexParameteri(GL_TEXTURE_2D, GL_DEPTH_TEXTURE_MODE_ARB, GL_INTENSITY)
        #Set alpha test to discard false comparisons
        glAlphaFunc(GL_NOTEQUAL, 0.0)

    def render_shadow_compare_after(self):
        blank_texture.bind()
        glDisable(GL_TEXTURE_GEN_S)
        glDisable(GL_TEXTURE_GEN_T)
        glDisable(GL_TEXTURE_GEN_R)
        glDisable(GL_TEXTURE_GEN_Q)
        glAlphaFunc(GL_GEQUAL, .5)
