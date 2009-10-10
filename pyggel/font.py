"""
pyggel.font
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The font module contains classes to display text images.
"""

from include import *
import image, view, data, misc, math3d
from scene import BaseSceneObject

class FontImage(BaseSceneObject):
    def __init__(self, font, text, size, color=(1,1,1,1),
                 underline=False, italic=False, bold=False,
                 linewrap=None, break_words=False):
        BaseSceneObject.__init__(self)
        self.font = font
        self.size = size
        self._bold = bold
        self._italic = italic
        self._underline = underline
        self.underline_count = 0
        self._color = None
        self._linewrap = linewrap
        self._break_words = break_words

        if underline:
            tsize = len(text)+1 #works because new lines are replaced by the underlines...
        else:
            tsize = len(text)-text.count("\n")

        self.text_array = data.get_best_array_type(GL_TRIANGLES, 6*tsize, 5) #create array!
        self.text_array.texture = self.font.font_tex

        self.text = text
        self.color = color

    def get_next_index(self, text, i):
        space = text.find(" ", i)
        new = text.find("\n", i)
        if (space, new) == (-1,-1):
            return -1
        if space == -1:
            return new
        if new == -1:
            return space
        return min((space, new))

    def set_text(self, text, color=(1,1,1,1)):
        if text == "":
            text = "\a"
        self._text = text

        new_size = (len(text)-text.count("\n")) * 6
        if new_size != self.text_array.max_size:
            self.text_array.resize(new_size)

        x = 0
        y = 0
        max_size = 0
        max_width = 0

        LW = self.linewrap
        BW = self.break_words

        g = self.size

        fin_size = self.font.get_size(text, g, self.bold, self.italic, LW)
        xf2, yf2 = fin_size[0]*0.5, fin_size[1]*0.5
        x, y = -xf2, -yf2

        if self.italic:
            skew = g / 10.0
        else:
            skew = 0
        if self.bold:
            warp = g / 4.0
            skew *= 2
        else:
            warp = 0

        last = None

        verts = []
        texcs = []

        uverts = [] #so we always put them last!
        utexcs = []
        self.underline_count = 0

        for i in xrange(len(text)):
            ti = text[i]
            if ti == "\n":
                uverts.extend([(-xf2,y+max_size,0), (-xf2,y+max_size+1,0), (x,y+max_size+1,0),
                              (-xf2,y+max_size,0), (x,y+max_size+1,0), (x,y+max_size,0)])
                utexcs.extend([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)])
                self.underline_count += 1
                x = -xf2
                y += max_size
                max_size = 0
                last = ti
                continue
            if LW and last in (" ", "\n") and self.get_next_index(text, i)>=0 and\
               self.font.get_size(text[i:self.get_next_index(text, i)], g, self.bold, self.italic)[0]+xf2 > LW:
                uverts.extend([(-xf2,y+max_size,0), (-xf2,y+max_size+1,0), (x,y+max_size+1,0),
                              (-xf2,y+max_size,0), (x,y+max_size+1,0), (x,y+max_size,0)])
                utexcs.extend([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)])
                self.underline_count += 1
                x = -xf2
                y += max_size
                max_size = 0
            elif LW and BW and x+xf2 > LW:
                uverts.extend([(-xf2,y+max_size,0), (-xf2,y+max_size+1,0), (x,y+max_size+1,0),
                              (-xf2,y+max_size,0), (x,y+max_size+1,0), (x,y+max_size,0)])
                utexcs.extend([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)])
                self.underline_count += 1
                x = -xf2
                y += max_size
                max_size = 0
            if ti in self.font.renderable:
                tsx, tsy, tex, tey, w, h = self.font.font_mapping[ti]
            else:
                tsx, tsy, tex, tey, w, h = self.font.font_mapping["\a"]

            w = g * (w*1.0/h)
            h = g

            verts.extend([(x+skew,y,0),
                          (x-skew,y+h,0),
                          (x+w+warp-skew,y+h,0),
                          (x+skew,y,0),
                          (x+w+warp-skew,y+h,0),
                          (x+w+skew+warp,y,0)])

            texcs.extend([(tsx, 1-tsy),
                          (tsx, 1-tey),
                          (tex, 1-tey),
                          (tsx, 1-tsy),
                          (tex, 1-tey),
                          (tex, 1-tsy)])

            x += w+warp+skew
            max_size = max((max_size, h))

            last = ti

        #so we have the last underline!
        uverts.extend([(-xf2,y+max_size,0), (-xf2,y+max_size+1,0), (x,y+max_size+1,0),
                      (-xf2,y+max_size,0), (x,y+max_size+1,0), (x,y+max_size,0)])
        utexcs.extend([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)])
        self.underline_count += 1

        self.text_array.reset_verts(verts+uverts)
        self.text_array.reset_texcs(texcs+utexcs)
        self.color = color

        self.width, self.height = fin_size

        self.offset = self.width*0.5, self.height*0.5

    def get_text(self):
        return self._text

    text = property(get_text, set_text)

    def set_color(self, color=(1,1,1,1)):
        t = numpy.array(color, "f")
        ltex = len(self.text) - self.text.count("\n")
        if t.shape == (4,): #single solid color
            color = [color]*ltex
        elif t.shape[0] < ltex:
            color += [color[0]] * ltex-len(color)
        if self.underline:
            color += [color[0]]*self.underline_count
        if color == self._color:
            return
        self._color = color

        _c = []

        for i in xrange(len(self.text)-self.text.count("\n")):
            for j in xrange(6):
                _c.append(color[i])
        self.text_array.reset_colors(_c)

    def get_color(self):
        return self._color

    color = property(get_color, set_color)

    def set_bold(self, bold):
        if bold == self._bold:
            return
        self._bold = bold
        self.set_text(self.text, self.color)
    def get_bold(self):
        return self._bold

    def set_italic(self, italic):
        if italic == self._italic:
            return
        self._italic = italic
        self.set_text(self.text, self.color)
    def get_italic(self):
        return self._italic

    def set_underline(self, underline):
        if underline == self._underline:
            return
        self._underline = underline
        self.set_text(self.text, self.color)
    def get_underline(self):
        return self._underline

    bold = property(get_bold, set_bold)
    italic = property(get_italic, set_italic)
    underline = property(get_underline, set_underline)

    def set_linewrap(self, linewrap):
        if linewrap == self._linewrap:
            return
        self._linewrap = linwrap
        self.set_text(self.text, self.color)
    def get_linewrap(self):
        return self._linewrap

    linewrap = property(get_linewrap, set_linewrap)

    def set_break_words(self, break_words):
        if break_words == self._break_words:
            return
        self._break_words = break_words
        self.set_text(self.text, self.color)
    def get_break_words(self):
        return self._break_words

    break_words = property(get_break_words, set_break_words)

    def render(self, camera=None):
        ox, oy = self.offset
        pos = self.pos

        glPushMatrix()
        glTranslatef(pos[0]+ox, pos[1]+oy, 0)

        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)

        try:
            glScalef(self.scale[0], self.scale[1], 1)
        except:
            glScalef(self.scale, self.scale, 1)

        self.text_array.render()
        glPopMatrix()

    def copy(self):
        a = FontImage(self.font, self.text, self.size, self.color, self.italic, self.bold, self.linewrap, self.break_words)
        a.pos = self.pos
        a.scale = self.scale
        a.rotation = self.rotation
        a.visible = self.visible
        a.pickable = self.pickable
        a.outline = self.outline
        a.outline_size = self.outline_size
        a.outline_color = self.outline_color
        return a

class FontImage3D(FontImage):
    def __init__(self, font, text, size=1, color=(1,1,1,1),
                 underline=False, italic=False, bold=False,
                 linewrap=None, break_words=False):
        FontImage.__init__(self, font, text, size, color, underline, italic, bold, linewrap, break_words)

    def render(self, camera=None):
        pos = self.pos
        glPushMatrix()
        glTranslatef(pos[0], pos[1], -pos[2])
        if camera:
            camera.set_facing_matrix()
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)

        try:
            glScalef(self.scale[0], -self.scale[1], 1)
        except:
            glScalef(self.scale, -self.scale, 1)

        if view.screen.lighting:
            glDisable(GL_LIGHTING)
        self.text_array.render()
        if view.screen.lighting:
            glEnable(GL_LIGHTING)
        glPopMatrix()

    def copy(self):
        a = FontImage3D(self.font, self.text, self.size, self.color, self.italic, self.bold, self.linewrap, self.break_words)
        a.pos = self.pos
        a.scale = self.scale
        a.rotation = self.rotation
        a.visible = self.visible
        a.pickable = self.pickable
        a.outline = self.outline
        a.outline_size = self.outline_size
        a.outline_color = self.outline_color
        return a

class Font(object):
    renderable = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./ " +\
                 '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'
    def __init__(self, filename=None, font_size=32, font_size3d=0.1, internal_font_size=64):
        view.require_init()

        self.filename = filename
        self.font_obj = pygame.font.Font(self.filename, internal_font_size)
        self.font_size = font_size
        self.font_size3d = font_size3d

        self._build_tex()

    def _build_tex(self):
        chars = self.renderable + "\a"
        mapping = {}
        x = 0
        y = 0
        max_height = 0

        pyg_im = pygame.Surface((512,512)).convert_alpha()
        pyg_im.fill((0,0,0,0))

        for i in chars:
            g = self.font_obj.render(i, True, (255,255,255))
            tdata = pygame.image.tostring(g, "RGBA", 1)
            xs, ys = g.get_size()
            if x + xs >= 512:
                x = 0
                y += max_height
                max_height = 0
            if y+ys >= 512:
                raise Exception("Ran out of room for Font texture map - reduce internal_font_size when creating font.")

            max_height = max((max_height, ys))

            pyg_im.blit(g, (x,y))

            mapping[i] = (math3d.safe_div(x, 512.0),#tex start x
                          math3d.safe_div(y, 512.0),#tex start y
                          math3d.safe_div(x+xs, 512.0),#tex end x
                          math3d.safe_div(y+ys, 512.0),#tex end y
                          xs,#width
                          ys)#height

            x += xs
        pygame.draw.line(pyg_im, (255,255,255), (0,511), (511,511))

        self.font_tex = data.Texture(pyg_im)
        self.font_mapping = mapping
        self.font_image = image.Image(pyg_im)

    def get_size(self, text, size, bold=False, italic=False, linewrap=None):
        x = y = max_size = max_width = 0
        for i in xrange(len(text)):
            ti = text[i]
            if ti == "\n":
                x = 0
                y += max_size
                max_size = 0
                continue
            if linewrap and x > linewrap:
                x = 0
                y += max_size
                max_size = 0
            if ti in self.font_mapping:
                tsx, tsy, tex, tey, w, h = self.font_mapping[ti]
            else:
                tsx, tsy, tex, tey, w, h = self.font_mapping["\a"]

            w = size * (w*1.0/h)
            h = size

            if italic:
                w += size/10.0
            if bold:
                w += size/4.0
                if italic:
                    w += size/10.0

            x += w
            max_size = max((max_size, h))
            max_width = max((max_width, x))

        if italic:
            max_width += size/10.0 #because it is subtracted on left of each glyph as well!
            if bold:
                max_width += size/10.0

        return max_width, y+max_size

    def make_text_image2D(self, text, color=(1,1,1,1), underline=False, italic=False,
                          bold=False, linewrap=None, break_words=False, override_size=None):
        if override_size:
            size = override_size
        else:
            size = self.font_size
        return FontImage(self, text, size, color, underline, italic, bold, linewrap, break_words)

    def make_text_image3D(self, text, color=(1,1,1,1), underline=False, italic=False,
                          bold=False, linewrap=None, break_words=False, override_size=None):
        if override_size:
            size = override_size
        else:
            size = self.font_size3d
        return FontImage3D(self, text, size, color, underline, italic, bold, linewrap, break_words)
            
