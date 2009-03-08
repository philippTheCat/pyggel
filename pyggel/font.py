"""
pyggle.font
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The font module contains classes to display text images.
"""

from include import *
import image, view

class Font(object):
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

    def make_text_image(self, text="", color=(1,1,1,1)):
        """Create an image.Image object with the text rendered to it.
           text is the text to render
           color is the color of the text (0-1 RGBA)"""
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
            return image.Image(new, colorize=color)
            
        else:
            return image.Image(self.pygame_font.render(text, True, (255,255,255)),
                               colorize=color)

    def make_text_image3D(self, text="", color=(1,1,1,1)):
        """Create an image.Image3D object with the text rendered to it.
           text is the text to render
           color is the color of the text (0-1 RGBA)"""
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
            return image.Image3D(new, colorize=color)
        else:
            return image.Image3D(self.pygame_font.render(text, True, (255,255,255)),
                                 colorize=color)

class MEFontImage(object):
    """A font image that renders more slowly,
       but supports changing of text on the fly (very slowly though)
       among other features (like smilies)"""
    def __init__(self, fontobj, text="", colorize=(1,1,1,1)):
        """Create the text
           fontobj is the MEFont object that created this text
           text is the text string to render
           colorize is the color (0-1 RGBA) of the text"""
        self.fontobj = fontobj
        self.rotation = (0,0,0)
        self.scale = 1
        self.visible = True

        self._pos = (0,0)
        self._colorize = (1,1,1,1)
        self.glyphs = []
        self._comp_glyphs = []

        self.colorize = colorize
        self.pos = (0,0)
        self.text = text

    def get_text(self):
        return self._text
    def set_text(self, text):
        self._text = text
        self.glyphs = self.make_list_of_glyphs_and_smileys(text)
        n = [[]]
        height = 0
        for i in self.glyphs:
            if i == "\n":
                n[-1] = [n[-1], height]
                height = 0
                n.append([])
            else:
                n[-1].append(i)
                if i.get_height() > height:
                    height = i.get_height()
        n[-1] = [n[-1], height]
        self.glyphs = n
        self.compile_glyphs()
    text = property(get_text, set_text)
    def compile_glyphs(self):
        self._comp_glyphs = []
        downdent = 0
        for line in self.glyphs:
            line, height = line
            indent = 0
            for glyph in line:
                x, y = self.pos
                x += indent
                y += downdent
                glyph.pos = (x, y)
                indent += glyph.get_width()
                self._comp_glyphs.append(glyph)
            downdent += height
    def get_pos(self):
        return self._pos
    def set_pos(self, pos):
        self._pos = pos
        self.compile_glyphs()
    pos = property(get_pos, set_pos)
    def get_col(self):
        return self._colorize
    def set_col(self, col):
        self._colorize = col
        for glyph in self._comp_glyphs:
            glyph.colorize = self._colorize
    colorize = property(get_col, set_col)

    def make_list_of_glyphs_and_smileys(self, text):
        g = []
        skip = 0
        num = 0
        smiley_positions = {}
        for s in self.fontobj.smileys:
            last = 0
            while 1:
                n = text.find(s, last)
                if n >= 0:
                    smiley_positions[n] = s
                    last = n + len(s)
                else:
                    break

        for i in text:
            if skip:
                skip -= 1
            elif num in smiley_positions:
                a = smiley_positions[num]
                g.append(self.fontobj.smileys[a].copy())
                skip = len(a)-1
            elif i == "\n":
                g.append(i)
            else:
                g.append(self.fontobj.glyphs[i].copy())
            num += 1
        return g

    def render(self, camera=None):
        """Render the object
           camera can be None or the camera object used in the scene to render this
               Only here to maintain compatability with other 2d gfx"""
        fo = self.fontobj
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
        for glyph in self._comp_glyphs:
            glyph.render()
        glPopMatrix()

    def copy(self):
        """Copy the text image"""
        n = MEFontImage(self.fontobj, self.text, self.colorize)
        n.pos = self.pos
        n.rotation = self.rotation
        n.scale = self.scale
        n.visible = self.visible
        return n

    def get_width(self):
        """Return the max width of the text - in pixels"""
        width = 0
        for line in self.glyphs:
            line = line[0]
            indent = 0
            for glyph in line:
                indent += glyph.get_width()
            if indent > width:
                width = indent
        return width
                

    def get_height(self):
        """return the max height of the text - in pixels"""
        downdent = 0
        for line in self.glyphs:
            downdent += line[1]
        return downdent

    def get_size(self):
        """Return the size of the text - in pixels"""
        return (self.get_width(), self.get_height())

    def get_rect(self):
        """Return a pygame.Rect of the font image"""
        return pygame.rect.Rect(self.pos, self.get_size())

class MEFont(object):
    """A font the produces text images that render a little slower, but are much faster to change text,
       and support image 'smilies'"""
    def __init__(self, filename=None, fsize=32):
        """Create the font object
           filename can be None or the filename of the font to load (TTF)
           fsize is the size of the font
           smilies is a dict of name:image smilies"""
        view.require_init()
        self.filename = filename
        self.fsize = fsize

        self.smileys = {}

        self.acceptable = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`1234567890-=+_)(*&^%$#@!~[]\\;',./<>?:\"{}| "
        self._load_font()

    def add_smiley(self, name, smiley):
        """Add a smiley to the font.
           smiley must be a pygame.Surface, the path to an image or a pyggel.image.Image.
           Smileys are used in text by writing '[smiley_name]some text'"""
        if isinstance(smiley, image.Image) or\
           isinstance(smiley, image.Animation):
            self.smileys[name] = smiley
        else:
            self.smileys[name] = image.Image(smiley)

    def _load_font(self):
        """Load the font, and create glyphs"""
        self.pygame_font = pygame.font.Font(self.filename, self.fsize)

        L = {}
        for i in self.acceptable:
            L[i] = image.Image(self.pygame_font.render(i, True, (255,255,255)))

        self.glyphs = L

    def make_text_image(self, text="", color=(1,1,1,1)):
        """Return a MEFontImage that holds the text
           text is the text to render
           color = the color of the text (0-1 RGBA)"""
        return MEFontImage(self, text, color)

class MEFont2Image(object):
    def __init__(self, font, text, color, linewrap=None):
        self._font = font
        self._text = text
        self._color = color
        self._linewrap = linewrap

        self.pos = (0,0)
        self.rotation = (0,0,0)

        self.size = (0,0)
        self.scale = 1
        self.visible = True
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
    font = property(getfont, setfont)
    text = property(gettext, settext)
    color = property(getcolor, setcolor)
    linewrap = property(getlinewrap, setlinewrap)

    def rebuild_glyphs(self):
        glyphs = []
        indent = 0
        downdent = 0
        newh = self.font.fontobj.get_height()
        space = int(self.font.size / 3)
        linewrap = self.linewrap

        _w = 0
        for line in self.text.split("\n"):
            for word in line.split(" "):
                if word in self.font.images:
                    i = self.font.images[word].copy()
                else:
                    i = image.Image(self.font.fontobj.render(word, True, (255,255,255)))
                glyphs.append(i)
                w, h = i.get_size()
                if linewrap and indent and indent+w > linewrap:
                    if indent - space > _w:
                        _w = indent - space
                    indent = 0
                    downdent += newh
                    newh = 0
                i.pos = (indent, downdent)
                i.colorize = self.color
                indent += w + space
                if h > newh:
                    newh = h
            if indent - space > _w:
                _w = indent - space
            indent = 0
            downdent += newh
            newh = 0

        self.glyphs = glyphs
        self.size = (_w, downdent)

    def get_width(self):
        return self.size[0]
    def get_height(self):
        return self.size[1]
    def get_size(self):
        return self.size
    def get_rect(self):
        return pygame.rect.Rect(self.pos, self.size)

    def copy(self):
        new = MEFont2Image(self.font, self.text, self.color, self.linewrap)
        new.visible = self.visible
        new.scale = self.scale
        new.pos = self.pos
        new.rotation = self.rotation
        new.size = self.size

    def render(self, camera=None):

        glPushMatrix()
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        try:
            glScalef(self.scale[0], self.scale[1], 1)
        except:
            glScalef(self.scale, self.scale, 1)
        for glyph in self.glyphs:
            glyph.render()
        glPopMatrix()

class MEFont2(object):
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
        self.fontobj = pygame.font.Font(self.filename, self.size)

    def make_text_image(self, text="", color=(1,1,1,1)):
        return MEFont2Image(self, text, color)

    def add_image(self, name, image):
        self.images[name] = image
