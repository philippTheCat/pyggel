import Image
import pygame
from pygame.locals import *

import time

def get_all_frames(image):
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
            if len(image.tile) > 0:
                x0, y0, x1, y1 = image.tile[0][1]

                if image.tile[0][3][0] == 4:
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


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))

    src_image = Image.open("data/hulk.gif")
    src_image2 = Image.open("data/football.gif")
    surfs = get_all_frames(src_image)
    surfs2 = get_all_frames(src_image2)
    cur = 0
    ptime = time.time()

    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return

        screen.fill((255,255,255))
        if time.time() - ptime > surfs[cur][1]:
            cur += 1
            if cur >= len(surfs):
                cur = 0
            ptime = time.time()

        screen.blit(surfs[cur][0], (50, 50))
        screen.blit(surfs2[43][0], (100,50))
        pygame.display.flip()

main()
