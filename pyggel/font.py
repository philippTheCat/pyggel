"""
pyggle.font
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The font module contains classes to display text images.
"""

from include import *
import image, view, data

class Font3D(object):
    """A font object used for rendering text to images"""
    def __init__(self, filename=None, fsize=32):
        """Create the font
           filename can be None or the filename of the font to load (TTF)
           fsize is the size of the font"""
        view.require_init()
        self.filename = filename
        self.fsize = fsize
        self.fontname = str(self.filename) + ":" + str(self.fsize)

        self._load_font()

    def _load_font(self):
        """Load the font"""
        self.pygame_font = pygame.font.Font(self.filename, self.fsize)

    def make_text_image(self, text="", color=(1,1,1,1), underline=False, italic=False, bold=False):
        """Create an image.Image3D object with the text rendered to it.
           text is the text to render
           color is the color of the text (0-1 RGBA)"""
        self.pygame_font.set_underline(underline)
        self.pygame_font.set_italic(italic)
        self.pygame_font.set_bold(bold)
        if "\n" in text:
            text = text.split("\n")
            n = []
            h = self.pygame_font.get_height()
            w = 0
            tot = 0
            for i in text:
                n.append(self.pygame_font.render(i, True, (255, 255, 255)))
                nw = n[-1].get_width()
                if nw > w:
                    w = nw
                tot += h
            new = pygame.Surface((w, tot)).convert_alpha()
            new.fill((0,0,0,0))
            tot = 0
            for i in n:
                new.blit(i, (0, tot*h))
                tot += 1
            self.pygame_font.set_underline(False)
            self.pygame_font.set_italic(False)
            self.pygame_font.set_bold(False)
            return image.Image3D(new, colorize=color)
        else:
            a = self.pygame_font.render(text, True, (255,255,255))
            self.pygame_font.set_underline(False)
            self.pygame_font.set_italic(False)
            self.pygame_font.set_bold(False)
            return image.Image3D(a, colorize=color)


class FontImage(object):
    def __init__(self, font, text, color, linewrap=None, underline=False, italic=False, bold=False):
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
        self.visible = True

        self._compiled = False
        self._compiled_list = None
        self._compiled_glyphs = []

        self.rebuild_glyphs()

    def getfont(self):
        return self._font
    def setfont(self, font):
        self._font = font
        self.rebuild_glyphs()
    def gettext(self):
        return self._text
    def settext(self, text):
        self._text = text
        self.rebuild_glyphs()
    def getcolor(self):
        return self._color
    def setcolor(self, color):
        self._color = color
        self.rebuild_glyphs()
    def getlinewrap(self):
        return self._linewrap
    def setlinewrap(self, linewrap):
        self._linewrap = linewrap
        self.rebuild_glyphs()
    def getunderline(self):
        return self._underline
    def setunderline(self, underline):
        self._underline = underline
        self.rebuild_glyphs()
    def getitalic(self):
        return self._italic
    def setitalic(self, italic):
        self._italic = italic
        self.rebuild_glyphs()
    def getbold(self):
        return self._bold
    def setbold(self, bold):
        self._bold = bold
        self.rebuild_glyphs()
    underline = property(getunderline, setunderline)
    italic = property(getitalic, setitalic)
    bold = property(getbold, setbold)
    font = property(getfont, setfont)
    text = property(gettext, settext)
    color = property(getcolor, setcolor)
    linewrap = property(getlinewrap, setlinewrap)

    def compile(self):
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
        self._compiled = False
        self._compiled_list = None
        self._compiled_glyphs = []

    def rebuild_glyphs(self):
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
        return self.size[0]
    def get_height(self):
        return self.size[1]
    def get_size(self):
        return self.size
    def get_rect(self):
        return pygame.rect.Rect(self.pos, self.size)

    def copy(self):
        new = FontImage(self.font, self.text, self.color, self.linewrap)
        new.visible = self.visible
        new.scale = self.scale
        new.pos = self.pos
        new.rotation = self.rotation
        new.size = self.size

    def render(self, camera=None):

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
        for glyph in g:
            glyph.render()
        glPopMatrix()

class Font(object):
    def __init__(self, filename=None, size=32):
        view.require_init()
        self._filename = filename
        self._size = size

        self.rebuild_font()

        self.images = {}

    def getf(self):
        return self._filename
    def setf(self, filename):
        self._filename = filename
        self.rebuild_font()
    filename = property(getf, setf)

    def gets(self):
        return self._size
    def sets(self, size):
        self._size = size
        self.rebuild_font()
    size = property(gets, sets)

    def rebuild_font(self):
        self.pygame_font = pygame.font.Font(self.filename, self.size)

    def make_text_image(self, text="", color=(1,1,1,1), linewrap=None, underline=False, italic=False, bold=False):
        return FontImage(self, text, color, linewrap, underline, italic, bold)

    def add_image(self, name, img):
        if isinstance(img, image.Image) or\
           isinstance(img, image.Animation):
            self.images[name] = img
        else:
            if img.split(".")[-1] in ("gif", "GIF"):
                self.images[name] = image.GIFImage(img)
            else:
                self.images[name] = image.Image(img)

class MEFontImage(object):
    """A font image that renders more slowly,
       but supports changing of text on the fly (very slowly though)
       among other features (like smilies)"""
    def __init__(self, font, text="", colorize=(1,1,1,1), linewrap=None,
                 underline=False, italic=False, bold=False):
        """Create the text
           font is the MEFont object that created this text
           text is the text string to render
           colorize is the color (0-1 RGBA) of the text"""
        self.font = font
        self.rotation = (0,0,0)
        self.scale = 1
        self.visible = True

        self._underline = underline
        self._italic = italic
        self._bold = bold

        self.linewrap = linewrap

        self.pos = (0,0)
        self._colorize = (1,1,1,1)
        self.glyphs = []
        self._width = 0
        self._height = 0

        self.colorize = colorize
        self.pos = (0,0)
        self.text = text

    def get_text(self):
        return self._text
    def set_text(self, text):
        self._text = text
        gg = self.make_list_of_glyphs_and_images(text)
        g = []
        indent = 0
        downdent = 0
        newh = 0
        self._width = 0
        for i in gg:
            if i =="\n":
                if indent > self._width:
                    self._width = indent
                indent = 0
                downdent += newh
                newh = 0
            else:
                if self.linewrap and indent and indent + i.get_width() > self.linewrap:
                    if indent > self._width:
                        self._width = indent
                    indent = 0
                    downdent += max((newh, i.get_height()))
                    newh = 0
                newh = max((newh, i.get_height()))
                i.pos = (indent, downdent)
                g.append(i)
                indent += i.get_width()
        self._height = downdent
        self.glyphs = g
        self.set_col(self._colorize)
    text = property(get_text, set_text)

    def getunderline(self):
        return self._underline
    def setunderline(self, underline):
        self._underline = underline
        self.set_text(self._text)
    def getitalic(self):
        return self._italic
    def setitalic(self, italic):
        self._italic = italic
        self.set_text(self._text)
    def getbold(self):
        return self._bold
    def setbold(self, bold):
        self._bold = bold
        self.set_text(self._text)
    underline = property(getunderline, setunderline)
    italic = property(getitalic, setitalic)
    bold = property(getbold, setbold)

    def get_col(self):
        return self._colorize
    def set_col(self, col):
        self._colorize = col
        for glyph in self.glyphs:
            glyph.colorize = self._colorize
    colorize = property(get_col, set_col)

    def make_list_of_glyphs_and_images(self, text):
        g = []
        skip = 0
        num = 0
        image_positions = {}
        ss = self.font.images
        cols = ""
        if self._underline:
            cols += "u"
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
        """Render the object
           camera can be None or the camera object used in the scene to render this
               Only here to maintain compatability with other 2d gfx"""
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
        for glyph in self.glyphs:
            glyph.render()
        glPopMatrix()

    def copy(self):
        """Copy the text image"""
        n = MEFontImage(self.font, self.text, self.colorize)
        n.pos = self.pos
        n.rotation = self.rotation
        n.scale = self.scale
        n.visible = self.visible
        return n

    def get_width(self):
        """Return the max width of the text - in pixels"""
        return self._width   

    def get_height(self):
        """return the max height of the text - in pixels"""
        return self._height

    def get_size(self):
        """Return the size of the text - in pixels"""
        return (self._width, self._height)

    def get_rect(self):
        """Return a pygame.Rect of the font image"""
        return pygame.rect.Rect(self.pos, self.get_size())

class MEFont(object):
    """A font that supports more efficient changing of text."""
    def __init__(self, filename=None, fsize=32):
        """Create the font object
           filename can be None or the filename of the font to load (TTF)
           fsize is the size of the font
           smilies is a dict of name:image smilies"""
        view.require_init()
        self.filename = filename
        self.fsize = fsize

        self.images = {}

        self.acceptable = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`1234567890-=+_)(*&^%$#@!~[]\\;',./<>?:\"{}| "
        self._load_font()

    def add_image(self, name, img):
        """Add an image to the font.
           img must be a pygame.Surface, the path to an image or a pyggel.image.Image.
           Images are used by simply adding the string 'name' to the text"""
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
        self.pygame_font = pygame.font.Font(self.filename, self.fsize)

        L = {}
        Lu = {}
        Lui = {}
        Luib = {}
        Lub = {}
        Lb = {}
        Lib = {}
        Li = {}
        for i in self.acceptable:
            L[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_underline(True)
        for i in self.acceptable:
            Lu[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_italic(True)
        for i in self.acceptable:
            Lui[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_bold(True)
        for i in self.acceptable:
            Luib[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_italic(False)
        for i in self.acceptable:
            Lub[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_underline(False)
        for i in self.acceptable:
            Lb[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_italic(True)
        for i in self.acceptable:
            Lib[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_bold(False)
        for i in self.acceptable:
            Li[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))
        self.pygame_font.set_italic(False)

        self.glyphs = {"": L,
                       "u":Lu,
                       "ui":Lui,
                       "uib":Luib,
                       "ub":Lub,
                       "b":Lb,
                       "i":Li,
                       "ib":Lib}

    def make_text_image(self, text="", color=(1,1,1,1), linewrap=None, underline=False, italic=False, bold=False):
        """Return a MEFontImage that holds the text
           text is the text to render
           color = the color of the text (0-1 RGBA)"""
        return MEFontImage(self, text, color, linewrap, underline, italic, bold)
