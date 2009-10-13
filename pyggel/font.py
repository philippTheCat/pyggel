"""
pyggel.font
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The font module contains classes to display text images.
"""

from include import *
import image, view, data, misc, math3d
from scene import BaseSceneObject

class RFontImage(BaseSceneObject):
    """A font image that renders fast, but changing text is slow."""
    def __init__(self, font, text, color=(1,1,1,1), linewrap=None, underline=False, italic=False, bold=False):
        """Create the font image
           font must be the font object used to create this image
           text must be a string of text to render (support \n newlines)
           color must be the rgba(0-1) color of the image text
           linewrap must be None or the number of pixels wide a line *should* be
               if an individual word is too large then it will go over
           underline must be True/False - whether the text is underlined or not
           italic must be True/False - whether the text is italic or not
           bold must be True/False - whether the text is bold or not"""
        BaseSceneObject.__init__(self)

        self._font = font
        self._text = text
        self._color = color
        self._linewrap = linewrap
        self._underline = underline
        self._italic = italic
        self._bold = bold

        self.pos = (0,0)
        self.rotation = (0,0,0)

        self.size = (0,0)
        self.scale = 1

        self._compiled = False
        self._compiled_list = None
        self._compiled_glyphs = []

        self.rebuild_glyphs()

    def get_font(self):
        """Return font object used to create this image."""
        return self._font
    def set_font(self, font):
        """Set font object used to create this image - rebuilds text with new font."""
        self._font = font
        self.rebuild_glyphs()
    def get_text(self):
        """Returns text."""
        return self._text
    def set_text(self, text):
        """Sets text and updates image."""
        self._text = text
        self.rebuild_glyphs()
    def get_color(self):
        """Returns color."""
        return self._color
    def set_color(self, color):
        """Sets color and updates image."""
        self._color = color
        self.rebuild_glyphs()
    def get_linewrap(self):
        """Return linewrap."""
        return self._linewrap
    def set_linewrap(self, linewrap):
        """Sets linewrap and updates image."""
        self._linewrap = linewrap
        self.rebuild_glyphs()
    def get_underline(self):
        """Return underline."""
        return self._underline
    def set_underline(self, underline):
        """Sets underline and updates image."""
        self._underline = underline
        self.rebuild_glyphs()
    def get_italic(self):
        """Returns italic."""
        return self._italic
    def set_italic(self, italic):
        """Sets italic and updates image."""
        self._italic = italic
        self.rebuild_glyphs()
    def get_bold(self):
        """Returns bold."""
        return self._bold
    def set_bold(self, bold):
        """Sets bold and updates image."""
        self._bold = bold
        self.rebuild_glyphs()
    underline = property(get_underline, set_underline)
    italic = property(get_italic, set_italic)
    bold = property(get_bold, set_bold)
    font = property(get_font, set_font)
    text = property(get_text, set_text)
    color = property(get_color, set_color)
    linewrap = property(get_linewrap, set_linewrap)

    def compile(self):
        """Compile the text so rendering is even fast, but text/color/etc. is even slower."""
        self._compiled = True
        li = self._compiled_list
        gl = []
        if not li:
            li = data.DisplayList()

        li.begin()
        for i in self.glyphs:
            if isinstance(i, image.Image):
                i.render()
            else:
                gl.append(i)
        li.end()
        gl.append(li)
        self._compiled_glyphs = gl
        self._compiled_list = li

    def uncompile(self):
        """Uncompile text."""
        self._compiled = False
        self._compiled_list = None
        self._compiled_glyphs = []

    def rebuild_glyphs(self):
        """Recreate all glyphs to represent current state of text image."""
        glyphs = []
        indent = 0
        linewrap = self.linewrap

        px, py = self.pos

        self.font.pygame_font.set_underline(self._underline)
        self.font.pygame_font.set_italic(self._italic)
        self.font.pygame_font.set_bold(self._bold)

        skip = 0
        num = 0
        image_positions = {}
        text = self.text
        if self.font.images:
            for s in self.font.images:
                last = 0
                while 1:
                    n = text.find(s, last)
                    if n >= 0:
                        image_positions[n] = s
                        last = n + len(s)
                    else:
                        break
        if self.font.images and image_positions:
            word = ""
            indent = 0
            downdent = 0
            newh = 0
            _w = 0
            for i in text:
                if skip:
                    skip -= 1
                    num += 1
                    continue
                elif num in image_positions:
                    if word:
                        i = image.Image(self.font.pygame_font.render(word, True, (255,255,255)))
                        i.colorize = self.color
                        w, h = i.get_size()
                        if linewrap and indent and indent+w > linewrap:
                            if indent > _w:
                                _w = indent
                            indent = 0
                            downdent += newh
                            newh = h
                        newh = max((newh, h))
                        i.pos = (indent, downdent)
                        indent += w
                        word = ""
                        glyphs.append(i)
                    a = image_positions[num]
                    i = self.font.images[a].copy()
                    w, h = i.get_size()
                    if linewrap and indent and indent+w > linewrap:
                        if indent > _w:
                            _w = indent
                        indent = 0
                        downdent += newh
                        newh = h
                    newh = max((newh, h))
                    i.pos = (indent, downdent)
                    indent += w
                    glyphs.append(i)
                    skip = len(a)-1
                elif i == "\n":
                    if indent > _w:
                        _w = indent
                    indent = 0
                    downdent += newh
                    newh = 0
                elif i == " " and linewrap and indent and (indent + self.font.pygame_font.get_size(word+" ")[0] > linewrap):
                    i = image.image(self.font.pygame_font.render(word, True, (255,255,255)))
                    i.colorize = self.color
                    i.pos = (indent, downdent)
                    w, h = i.get_size()
                    indent = 0
                    downdent += max((h, newh))
                    newh = 0
                    glyphs.append(i)
                else:
                    word += i
                num += 1


            if word:
                i = image.Image(self.font.pygame_font.render(word, True, (255,255,255)))
                i.colorize = self.color
                w, h = i.get_size()
                if linewrap and indent and indent+w > linewrap:
                    if indent > _w:
                        _w = indent
                    indent = 0
                    downdent += newh
                    newh = h
                newh = max((newh, h))
                i.pos = (indent, downdent)
                indent += w
                word = ""
                glyphs.append(i)
            if indent > _w:
                _w = indent
            if newh:
                downdent += newh

        else:
            indent = 0
            downdent = 0
            newh = 0
            _w = 0
            for line in text.split("\n"):
                _l = ""
                for word in line.split(" "):
                    if linewrap and indent and (indent+self.font.pygame_font.size(_l + " " + word)[0]  > linewrap):
                        i = image.Image(self.font.pygame_font.render(_l, True, (255,255,255)))
                        i.colorize = self.color
                        x, y = i.get_size()
                        i.pos = (indent, downdent)
                        downdent += newh
                        newh = y
                        indent += x
                        if indent > _w:
                            _w = int(indent)
                        indent = 0
                        glyphs.append(i)
                        _l = word
                    else:
                        if _l:
                            _l += " " + word
                        else:
                            _l += word
                i = image.Image(self.font.pygame_font.render(_l, True, (255,255,255)))
                i.colorize = self.color
                x, y = i.get_size()
                i.pos = (indent, downdent)
                downdent += max((newh, y))
                newh = 0
                indent += x
                if indent > _w:
                    _w = int(indent)
                indent = 0
                glyphs.append(i)

        self.glyphs = glyphs
        self.size = (_w, downdent)

        if self._compiled:
            self.compile()

        self.font.pygame_font.set_underline(False)
        self.font.pygame_font.set_italic(False)
        self.font.pygame_font.set_bold(False)

    def get_width(self):
        """Return width of the image."""
        return self.size[0]
    def get_height(self):
        """Return height of the image."""
        return self.size[1]
    def get_size(self):
        """Return width/height of the image."""
        return self.size
    def get_rect(self):
        """Return a pygame.Rect representing the pos/size of the image."""
        return pygame.rect.Rect(self.pos, self.size)

    def copy(self):
        """Returns a new RFontImage that is a copy of this image."""
        new = RFontImage(self.font, self.text, self.color, self.linewrap)
        new.visible = self.visible
        new.scale = self.scale
        new.pos = self.pos
        new.rotation = self.rotation
        new.size = self.size
        new._compiled = self._compiled
        new.rebuild_glyphs()
        return new

    def render(self, camera=None):
        """Render the image."""
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], 0)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        try:
            glScalef(self.scale[0], self.scale[1], 1)
        except:
            glScalef(self.scale, self.scale, 1)
        if self._compiled:
            g = self._compiled_glyphs
        else:
            g = self.glyphs
        if self.outline:
            misc.outline(misc.OutlineGroup(g), self.outline_color, self.outline_size)
        for glyph in g:
            glyph.render()
        glPopMatrix()

class MEFontImage(BaseSceneObject):
    """A font image that renders more slowly, but is very fast to change text"""
    def __init__(self, font, text="", color=(1,1,1,1), linewrap=None,
                 underline=False, italic=False, bold=False):
        """Create the font image
           font must be the font object used to create this image
           text must be a string of text to render (support \n newlines)
           color must be the rgba(0-1) color of the image text
           linewrap must be None or the number of pixels wide a line *should* be
               if an individual word is too large then it will go over
           underline must be True/False - whether the text is underlined or not
           italic must be True/False - whether the text is italic or not
           bold must be True/False - whether the text is bold or not"""
        BaseSceneObject.__init__(self)

        self._font = font
        self.rotation = (0,0,0)
        self.scale = 1

        self._underline = underline
        self._italic = italic
        self._bold = bold

        self._linewrap = linewrap

        self.pos = (0,0)
        self._color = (1,1,1,1)
        self.glyphs = []
        self._width = 0
        self._height = 0

        self.color = color
        self.pos = (0,0)
        self.text = text

    def get_font(self):
        """Return font object used to create this image."""
        return self._font
    def set_font(self, font):
        """Set font object used to create this image - rebuilds text with new font."""
        self._font = font
        self.set_text(self.text)
    font = property(get_font, set_font)

    def get_linewrap(self):
        """Return linewrap."""
        return self._linewrap
    def set_linewrap(self, linewrap):
        """Sets linewrap and updates image."""
        self._linewrap = linewrap
        self.set_text(self.text)
    linewrap = property(get_linewrap, set_linewrap)

    def get_text(self):
        """Returns text."""
        return self._text
    def set_text(self, text):
        """Sets text and updates image."""
        self._text = text
        gg = self.make_list_of_glyphs_and_images(text)
        g = []
        indent = 0
        downdent = 0
        newh = 0
        self._width = 0
        _u = []
        for i in gg:
            if i =="\n":
                if indent > self._width:
                    self._width = indent
                if self.underline:
                    size = int(self.font.size / 10)
                    pi = image.create_empty_image((indent, size), self._color)
                    pi.pos = (0, downdent+newh-size)
                    _u.append(pi)
                indent = 0
                downdent += newh
                newh = 0
            else:
                if self.linewrap and indent and indent + i.get_width() > self.linewrap:
                    if indent > self._width:
                        self._width = indent
                    if self.underline:
                        size = int(self.font.size / 10)
                        pi = image.create_empty_image((indent, size), self._color)
                        pi.pos = (0, downdent+newh-size)
                        _u.append(pi)
                    indent = 0
                    downdent += max((newh, i.get_height()))
                    newh = 0
                newh = max((newh, i.get_height()))
                i.pos = (indent, downdent)
                g.append(i)
                indent += i.get_width()
        downdent += newh
        self._width = max((self._width, indent))
        self._height = downdent
        if self.underline:
            size = int(self.font.size / 10)
            pi = image.create_empty_image((indent, size), self._color)
            pi.pos = (0, downdent+newh-size)
            _u.append(pi)
        g.extend(_u)
        self.glyphs = g
        self.set_col(self._color)
    text = property(get_text, set_text)


    def get_underline(self):
        """Return underline."""
        return self._underline
    def set_underline(self, underline):
        """Sets underline and updates image."""
        self._underline = underline
        self.set_text(self._text)
    def get_italic(self):
        """Returns italic."""
        return self._italic
    def set_italic(self, italic):
        """Sets italic and updates image."""
        self._italic = italic
        self.set_text(self._text)
    def get_bold(self):
        """Returns bold."""
        return self._bold
    def set_bold(self, bold):
        """Sets bold and updates image."""
        self._bold = bold
        self.set_text(self._text)
    underline = property(get_underline, set_underline)
    italic = property(get_italic, set_italic)
    bold = property(get_bold, set_bold)

    def get_col(self):
        """Returns color."""
        return self._color
    def set_col(self, col):
        """Sets color and updates image."""
        self._color = col
        for glyph in self.glyphs:
            glyph.colorize = self._color
    color = property(get_col, set_col)

    def make_list_of_glyphs_and_images(self, text):
        """Creates a list of text glyphs and embedded images representing text."""
        g = []
        skip = 0
        num = 0
        image_positions = {}
        ss = self.font.images
        cols = ""

        if self.italic:
            cols += "i"
        if self.bold:
            cols += "b"

        sg = self.font.glyphs[cols]

        for s in ss:
            last = 0
            sl = len(s)
            while 1:
                n = text.find(s, last)
                if n > 0:
                    image_positions[n] = s
                    last = n + sl
                else:
                    break

        for i in text:
            if skip > 0:
                skip -= 1
            elif num in image_positions:
                a = image_positions[num]
                g.append(ss[a].copy())
                skip = len(a)-1
            elif i == "\n":
                g.append(i)
            else:
                g.append(sg[i].copy())
            num += 1
        return g

    def render(self, camera=None):
        """Render the image."""
        fo = self.font
        glPushMatrix()
        glTranslatef(self.pos[0], self.pos[1], 0)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        try:
            glScalef(self.scale[0], self.scale[1], 1)
        except:
            glScalef(self.scale, self.scale, 1)
        downdent = 0
        if self.outline:
            misc.outline(misc.OutlineGroup(self.glyphs), self.outline_color, self.outline_size)
        for glyph in self.glyphs:
            glyph.render()
        glPopMatrix()

    def copy(self):
        """Returns a new MEFontImage that is a copy of this image."""
        n = MEFontImage(self.font, self.text, self.colorize)
        n.pos = self.pos
        n.rotation = self.rotation
        n.scale = self.scale
        n.visible = self.visible
        return n

    def get_width(self):
        """Return width of the image."""
        return self._width  

    def get_height(self):
        """Return height of the image."""
        return self._height

    def get_size(self):
        """Return width/height of the image."""
        return (self._width, self._height)

    def get_rect(self):
        """Return a pygame.Rect representing the pos/size of the image."""
        return pygame.rect.Rect(self.pos, self.get_size())

class RFont(object):
    """A font that produces image objects that render fast, but changing text is slow."""
    def __init__(self, filename=None, size=32):
        """Create the font
           filename must be None or the filename of the font to load
           size is the size of the font"""
        view.require_init()
        self._filename = filename
        self._size = size

        self.rebuild_font()

        self.images = {}

    def getf(self):
        """Return filename."""
        return self._filename
    def setf(self, filename):
        """Set filename and rebuild."""
        self._filename = filename
        self.rebuild_font()
    filename = property(getf, setf)

    def gets(self):
        """Return size."""
        return self._size
    def sets(self, size):
        """Set size and rebuild."""
        self._size = size
        self.rebuild_font()
    size = property(gets, sets)

    def rebuild_font(self):
        """Recreate the pygame font used."""
        self.pygame_font = pygame.font.Font(self.filename, self.size)

    def make_text_image(self, text="", color=(1,1,1,1), linewrap=None,
                        underline=False, italic=False, bold=False):
        """Create a RFontImage object with the text rendered to it.
           text is the text to render
           color is the color of the text (0-1 RGBA)
           linewrap can be None or the max width in pixels for each line of text
               NOTE: if a single word is too large, it will spill over
           underline must be True/False - whether to underline text
           italic must be True/False - whether to italicize text
           bold must be True/False - whether to bold text"""
        return RFontImage(self, text, color, linewrap, underline, italic, bold)

    def add_image(self, name, img):
        """Adds an embeddable image to the font.
           name must be the string sequence used in text to reference this image, ie:
               :) = 'data/smiley_image.png'
               Then when a text image is created with ':)' in it, it is converted into an image
           img must be the image.Image, image.Animation or filename of the image to load."""
        if isinstance(img, image.Image) or\
           isinstance(img, image.Animation):
            self.images[name] = img
        else:
            if img.split(".")[-1] in ("gif", "GIF"):
                self.images[name] = image.GIFImage(img)
            else:
                self.images[name] = image.Image(img)

class MEFont(object):
    """A font that produces image objects that render slower, but changing text is fast."""
    def __init__(self, filename=None, size=32):
        """Create the font
           filename must be None or the filename of the font to load
           size is the size of the font"""
        view.require_init()

        self._filename = filename
        self._size = size

        self.images = {}

        self.acceptable = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`1234567890-=+_)(*&^%$#@!~[]\\;',./<>?:\"{}| "
        self._load_font()


    def gets(self):
        """Return size."""
        return self._size
    def sets(self, size):
        "Set size and rebuild."""
        self._size = size
        self._load_font()
    size = property(gets, sets)
    def getf(self):
        """Return filename."""
        return self._filename
    def setf(self, filename):
        """Set filename and rebuild."""
        self._filename = filename
        self._load_font()
    filename = property(getf, setf)

    def add_image(self, name, img):
        """Adds an embeddable image to the font.
           name must be the string sequence used in text to reference this image, ie:
               :) = 'data/smiley_image.png'
               Then when a text image is created with ':)' in it, it is converted into an image
           img must be the image.Image, image.Animation or filename of the image to load."""
        if isinstance(img, image.Image) or\
           isinstance(img, image.Animation):
            self.images[name] = img
        else:
            if img.split(".")[-1] in ("gif", "GIF"):
                self.images[name] = image.GIFImage(img)
            else:
                self.images[name] = image.Image(img)

    def _load_font(self):
        """Load the font, and create glyphs"""
        self.pygame_font = pygame.font.Font(self.filename, self._size)

        L = {}

        Lb = {}
        Lib = {}
        Li = {}
        for i in self.acceptable:
            L[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_bold(True)
        for i in self.acceptable:
            Lb[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_italic(True)
        for i in self.acceptable:
            Lib[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_bold(False)
        for i in self.acceptable:
            Li[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_italic(False)

        self.glyphs = {"": L, "b":Lb, "i":Li, "ib":Lib}

    def make_text_image(self, text="", color=(1,1,1,1), linewrap=None,
                        underline=False, italic=False, bold=False):
        """Create an FontImage object with the text rendered to it.
           text is the text to render
           color is the color of the text (0-1 RGBA)
           linewrap can be None or the max width in pixels for each line of text
               NOTE: if a single word is too large, it will spill over
           underline must be True/False - whether to underline text
           italic must be True/False - whether to italicize text
           bold must be True/False - whether to bold text"""
        return MEFontImage(self, text, color, linewrap, underline, italic, bold)


class FontImage(BaseSceneObject):
    def __init__(self, font, text, char_height, color=(1,1,1,1),
                 underline=False, italic=False, bold=False,
                 linewrap=None, break_words=False):
        BaseSceneObject.__init__(self)
        self.font = font
        self.char_height = char_height
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

    def set_text(self, text, color=(1,1,1,1)):
        if text == "":
            text = "\a"
        self._text = text

        new_size = (len(text)-text.count("\n")) * 6
        if new_size != self.text_array.max_size:
            self.text_array.resize(new_size)

        max_size = 0
        max_width = 0

        LW = self.linewrap
        BW = self.break_words

        g = self.char_height
        if self.underline:
            ug = self.char_height * 0.1
        else:
            ug = 0

        fin_size = self.font.get_size_from_obj_atts(self, self.text)
        xf2, yf2 = fin_size[0]*0.5, fin_size[1]*0.5
        x, y = -xf2, -yf2

        if self.italic:
            skew = g * 0.1
        else:
            skew = 0
        if self.bold:
            warp = g * 0.25
            skew *= 2
        else:
            warp = 0

        last = None

        verts = []
        texcs = []

        uverts = [] #so we always put them last!
        utexcs = []
        self.underline_count = 1

        for i in xrange(len(text)):
            ti = text[i]
            if ti == "\n":
                if self.underline:
                    if last:
                        x -= w + warp + skew
                    uverts.extend([(-xf2,y+max_size,0), (-xf2,y+max_size+ug,0), (x,y+max_size+ug,0),
                                  (-xf2,y+max_size,0), (x,y+max_size+ug,0), (x,y+max_size,0)])
                    utexcs.extend([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)])
                self.underline_count += 1
                x = -xf2
                y += max_size+ug
                max_size = 0
                last = ti
                continue
            if LW and last in (" ", "\n") and self.font.get_next_index(text, i)>=0 and\
               self.font.get_size(text[i:self.font.get_next_index(text, i)], g, self.underline, self.italic, self.bold)[0]+xf2+x > LW:
                if self.underline:
                    if last:
                        x -= w + warp + skew
                    uverts.extend([(-xf2,y+max_size,0), (-xf2,y+max_size+ug,0), (x,y+max_size+ug,0),
                                  (-xf2,y+max_size,0), (x,y+max_size+ug,0), (x,y+max_size,0)])
                    utexcs.extend([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)])
                self.underline_count += 1
                x = -xf2
                y += max_size+ug
                max_size = 0
            elif LW and BW and x+xf2 > LW:
                if self.underline:
                    if last:
                        x -= w + warp + skew
                    uverts.extend([(-xf2,y+max_size,0), (-xf2,y+max_size+ug,0), (x,y+max_size+ug,0),
                                  (-xf2,y+max_size,0), (x,y+max_size+ug,0), (x,y+max_size,0)])
                    utexcs.extend([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)])
                self.underline_count += 1
                x = -xf2
                y += max_size+ug
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
        if self.underline:
            uverts.extend([(-xf2,y+max_size,0), (-xf2,y+max_size+ug,0), (x,y+max_size+ug,0),
                          (-xf2,y+max_size,0), (x,y+max_size+ug,0), (x,y+max_size,0)])
            utexcs.extend([(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)])

        self.text_array.reset_verts(verts+uverts)
        self.text_array.reset_texcs(texcs+utexcs)
        self.color = color

        self.width, self.height = fin_size
        self.size = fin_size

        self.offset = self.width*0.5, self.height*0.5

    def get_text(self):
        return self._text

    text = property(get_text, set_text)

    def set_color(self, color=(1,1,1,1)):
        t = numpy.array(color, "f")
        ltex = len(self.text) - self.text.count("\n")
        if t.shape == (4,): #single solid color
            color = [color]*ltex
            t = numpy.array(color, "f")
        if t.shape == (3,):
            color = [color+(1,)]*ltex
        if t.shape[0] < ltex:
            color += [color[0]] * (ltex-t.shape[0])
            t = numpy.array(color, "f")
        if t.shape[0] > ltex:
            color = color[0:ltex]
            t = numpy.array(color, "f")
        if self.underline:
            color += [color[0]]*self.underline_count
            t = numpy.array(color, "f")

        if color == self._color:
            return
        self._color = color

        _c = []

        for i in xrange(len(color)):
            for j in xrange(6):
                _c.append(color[i])
        self.text_array.reset_colors(_c)

    def get_color(self):
        return self._color

    color = property(get_color, set_color)
    colorize = property(get_color, set_color)

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
        a = FontImage(self.font, self.text, self.char_height, self.color,
                      self.underline, self.italic, self.bold,
                      self.linewrap, self.break_words)
        a.pos = self.pos
        a.scale = self.scale
        a.rotation = self.rotation
        a.visible = self.visible
        a.pickable = self.pickable
        return a

    def get_width(self):
        return self.width
    def get_height(self):
        return self.height
    def get_size(self):
        return self.size

class FontImage3D(FontImage):
    def __init__(self, font, text, char_height=1, color=(1,1,1,1),
                 underline=False, italic=False, bold=False,
                 linewrap=None, break_words=False):
        FontImage.__init__(self, font, text, char_height, color, underline, italic, bold, linewrap, break_words)

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
        a = FontImage3D(self.font, self.text, self.char_height, self.color,
                        self.underline, self.italic, self.bold,
                        self.linewrap, self.break_words)
        a.pos = self.pos
        a.scale = self.scale
        a.rotation = self.rotation
        a.visible = self.visible
        a.pickable = self.pickable
        return a

class Font(object):
    renderable = "`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./ " +\
                 '~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'
    def __init__(self, filename=None, font_char_height=32, font_char_height3d=0.1, internal_font_size=64):
        view.require_init()

        self.filename = filename
        self.font_obj = pygame.font.Font(self.filename, internal_font_size)
        self.font_char_height = font_char_height
        self.font_char_height3d = font_char_height3d

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

    def get_size_from_obj_atts(self, obj, text):
        return self.get_size(text, obj.char_height, obj.underline, obj.italic, obj.bold, obj.linewrap, obj.break_words)

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

    def get_size(self, text, char_height, underline=False, italic=False, bold=False, linewrap=None, break_words=False):
        max_size = 0
        max_width = 0

        LW = linewrap
        BW = break_words

        g = char_height
        if underline:
            ug = char_height * 0.1
        else:
            ug = 0

        x = y = 0

        if italic:
            skew = g * 0.1
        else:
            skew = 0
        if bold:
            warp = g * 0.25
            skew *= 2
        else:
            warp = 0

        last = None

        underline_count = 1

        for i in xrange(len(text)):
            ti = text[i]
            if ti == "\n":
                underline_count += 1
                x = 0
                y += max_size+ug
                max_size = 0
                last = ti
                continue
            if LW and last in (" ", "\n") and self.get_next_index(text, i)>=0 and\
               self.get_size(text[i:self.get_next_index(text, i)], g, underline, italic, bold)[0]+x > LW:
                underline_count += 1
                x = 0
                y += max_size+ug
                max_size = 0
            elif LW and BW and x > LW:
                underline_count += 1
                x = 0
                y += max_size+ug
                max_size = 0
            if ti in self.renderable:
                tsx, tsy, tex, tey, w, h = self.font_mapping[ti]
            else:
                tsx, tsy, tex, tey, w, h = self.font_mapping["\a"]

            w = g * (w*1.0/h)
            h = g

            x += w+warp+skew
            max_size = max((max_size, h))
            max_width = max((max_width, x - (w+warp+skew)))

            last = ti

        return max_width, max_size+y+ug

    def make_text_image2D(self, text, color=(1,1,1,1), underline=False, italic=False,
                          bold=False, linewrap=None, break_words=False, override_char_height=None):
        if override_char_height:
            size = override_char_height
        else:
            size = self.font_char_height
        return FontImage(self, text, size, color, underline, italic, bold, linewrap, break_words)

    def make_text_image3D(self, text, color=(1,1,1,1), underline=False, italic=False,
                          bold=False, linewrap=None, break_words=False, override_char_height=None):
        if override_char_height:
            size = override_char_height
        else:
            size = self.font_char_height3d
        return FontImage3D(self, text, size, color, underline, italic, bold, linewrap, break_words)
            
