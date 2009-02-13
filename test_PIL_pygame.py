import Image
import pygame
from pygame.locals import *

import time

def get_all_frames(filename):
    image = Image.open(filename)
    surfs = []
    pal = image.getpalette()
    base_palette = []
    for i in range(0, len(pal), 3):
        rgb = pal[i:i+3]
        base_palette.append(rgb)
    try:
        while 1:
            try:
                duration = image.info["duration"]
            except:
                duration = 100

            duration *= .001 #convert to milliseconds!

            x0, y0, x1, y1 = (0, 0) + image.size
            if image.tile:
                tile = image.tile
            else:
                image.seek(0)
                tile = image.tile
            if len(tile) > 0:
                x0, y0, x1, y1 = tile[0][1]

                if tile[0][3][0] == 4:
                    palette = base_palette
                else:
                    pal = image.getpalette()
                    palette = []
                    for i in range(0, len(pal), 3):
                        rgb = pal[i:i+3]
                        palette.append(rgb)
            else:
                palette = base_palette

            pi = pygame.image.fromstring(image.tostring(), image.size, image.mode)
            pi.set_palette(palette)
            pi.set_colorkey(image.info["transparency"])
            pi2 = pygame.Surface(image.size, SRCALPHA)
            pi2.blit(pi, (x0, y0), (x0, y0, x1-x0, y1-y0))

            surfs.append([pi2, duration])
            image.seek(image.tell()+1)
    except EOFError:
        pass

    return surfs

class GIFImage(object):
    def __init__(self, filename):
        self.filename = filename
        self.frames = get_all_frames(self.filename)

        self.cur = 0
        self.ptime = time.time()

        self.running = True
        self.breakpoint = len(self.frames)-1
        self.startpoint = 0

    def render(self, screen, pos):
        if self.running:
            if time.time() - self.ptime > self.frames[self.cur][1]:
                self.cur += 1
                if self.cur >= self.breakpoint:
                    self.cur = self.startpoint

                self.ptime = time.time()

        screen.blit(self.frames[self.cur][0], pos)

    def seek(self, num):
        self.cur = num
        if self.cur < 0:
            self.cur = 0
        if self.cur >= len(self.frames):
            self.cur = len(self.frames)-1

    def set_bounds(self, start, end):
        if start < 0:
            start = 0
        if start >= len(self.frames):
            start = len(self.frames) - 1
        if end < 0:
            end = 0
        if end >= len(self.frames):
            end = len(self.frames) - 1
        if end < start:
            end = start
        self.startpoint = start
        self.breakpoint = end

    def pause(self):
        self.running = False

    def play(self):
        self.running = True

    def rewind(self):
        self.seek(0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))

    hulk = GIFImage("data/hulk.gif")
    football = GIFImage("data/football.gif")
    hulk.set_bounds(0, 2)

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

        screen.fill((255,255,255))
        hulk.render(screen, (50, 50))
        football.render(screen, (200, 50))
        pygame.display.flip()

main()
