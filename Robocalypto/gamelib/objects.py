import pygame
from pygame.locals import *

import math, random

import pyggel
from pyggel.misc import ObjectGroup as Group
from pyggel.misc import ObjectInstance

def colliderect(a, b):
    return a[0] + a[2] > b[0] and b[0] + b[2] > a[0] and a[1] + a[3] > b[1] and b[1] + b[3] > a[1]

def collidepoint(p, r):
    if r[0] < p[0] and p[0] < r[0]+r[2]:
        if r[1] < p[1] and p[1] < r[1]+r[3]:
            return True
    return False

class Object(ObjectInstance):
    
    def __init__(self, groups):
        self.grid_color = [0, 0, 0]
        ObjectInstance.__init__(self, groups)
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)

class GameObject(Object):
    
    def __init__(self, game, obj=None, pos=[0, 0], rotation=0, height=0, color=[1, 1, 1, 1]):
        Object.__init__(self, self.groups)
        self.game = game
        self.scene = self.game.scene
        self.pos = [pos[0], pos[1]]
        self.rotation = rotation
        self.obj = obj
        self.height = height
        self.update_obj()
    
    def update_obj(self):
        if self.obj:
            self.obj.pos = (self.pos[0], self.height, self.pos[1])
            self.obj.rotation = (self.obj.rotation[0], self.rotation, self.obj.rotation[2])
    
    def move(self, amount, rotation):
        po=0.0174532925
        self.pos[0] -= math.sin(rotation[1]*po)*amount
        self.height += math.sin(rotation[0]*po)*amount
        self.pos[1] += math.cos(rotation[1]*po)*amount
        self.update_obj()
    
    def position(self, x, y, h=None):
        self.pos[0] = x
        self.pos[1] = y
        if h:
            self.height = h
    
    def rotate(self, dx, dy, dz):
        self.obj.rotation = (self.obj.rotation[0]+dx, self.obj.rotation[1]+dy, self.obj.rotation[2]+dz)
        self.rotation = self.obj.rotation[1]
    
    def rotate_to(self, x, y, z):
        self.obj.rotation = (x, y, z)
        self.rotation = self.obj.rotation[1]
    
    def update(self):
        self.update_obj()

class Player(GameObject):
    
    def __init__(self, game):
        GameObject.__init__(self, game, obj=None, pos=[10, 15], rotation=0, height=0)
        self.old_pos = list(self.pos)
        self.speed = 0.3
        self.rel_timer = 0
        
        self.gun = Gun(self.game, self)
        self.frame = 0

        self.lives = 3
        self.ammo = 100
        self.score = 0
        
    def update(self):
        self.gun.update_pos()
        self.frame += 1
        if self.frame > 360:
            self.frame = 0
        self.rel_timer -= 1
        self.old_pos = list(self.pos)
        
        key = pygame.key.get_pressed()
        if key[K_w]:
            self.move(self.speed, (0, -self.rotation))
        if key[K_s]:
            self.move(-self.speed, (0, -self.rotation))
        if key[K_a]:
            self.move(-self.speed, (0, -self.rotation-90))
        if key[K_d]:
            self.move(self.speed, (0, -self.rotation-90))
        if key[K_w] or key[K_s] or key[K_a] or key[K_d]:
            self.gun.height = math.sin(math.radians(self.frame)*8)/75 + self.gun.old_y
            self.gun.update_obj()
        else:
            self.gun.height = self.gun.old_y
        
        mb = pygame.mouse.get_pressed()
        if mb[0]:
            if self.rel_timer <= 0:
              
                #Initial shot position
                if self.ammo:
                    shotpos = [self.gun.pos[0], self.gun.height-0.1, self.gun.pos[1]]
                    shotpos[0] += math.sin(math.radians(self.rotation+90))*.06
                    shotpos[2] += math.cos(math.radians(self.rotation+90))*.06
                    shotpos[0] += math.sin(math.radians(self.rotation))*0.75
                    shotpos[2] += math.cos(math.radians(self.rotation))*0.75
                    Shot(self.game, [shotpos[0], shotpos[2]], -self.rotation, shotpos[1])
                    self.rel_timer = 8
                    GunFlash(self.game, shotpos)
                    self.ammo -= 1
        
        if self.rel_timer > 5:
            self.gun.height = self.gun.old_y + 0.025
        elif self.rel_timer == 5:
            self.gun.height = self.gun.old_y
            self.frame = 0
    
    def collide(self, rect):
        #Collide n' slide.
        if collidepoint(self.pos, rect):
            #print [self.pos[0] - self.old_pos[0], self.pos[1] - self.old_pos[1]]
            if self.old_pos[0] >= rect[0]+rect[2] or self.old_pos[0] <= rect[0]:
                self.pos[0] = self.old_pos[0]
            if self.old_pos[1] >= rect[1]+rect[3] or self.old_pos[1] <= rect[1]:
                self.pos[1] = self.old_pos[1]

class Gun(GameObject):
    
    def __init__(self, game, player):
        height = -0.25
        GameObject.__init__(self, game, obj=pyggel.mesh.OBJ("data/gun.obj", colorize=[0.2, 0.2, 0.2, 1]), 
                            pos=[10, 15], rotation=0, height=height)
        self.player = player
        self.obj.scale = 0.65
        self.rotate_to(0, 0, 0)
        self.scene.add_3d(self.obj)
        self.update_pos()
        self.old_y = height
    
    def update_pos(self):
        self.rotate_to(0, -self.player.rotation, 0)
        self.update_obj()
        self.pos = list(self.player.pos)
        self.move(0.175, (0, -self.player.rotation-90))
        self.move(1.0, (0, -self.player.rotation))
        self.update_obj()

class Shot(GameObject):
    main_obj = None
    
    def __init__(self, game, pos, angle, height):
        if not self.main_obj:
            self.main_obj = pyggel.mesh.OBJ("data/bullet.obj")
        obj = self.main_obj.copy()
        GameObject.__init__(self, game, obj=obj, pos=pos, rotation=angle+90, height=height)
        self.obj.scale = [5, 0.75, 0.75]
        self.scene.add_3d(self.obj)
        self.speed = 3.0
        
    def kill(self):
        if self.alive():
            GameObject.kill(self)
            self.scene.remove_3d(self.obj)
        
    def move_increment(self):
        self.move(self.speed/5, (0, self.rotation-90))

    def collide(self, rect):
        if collidepoint(self.pos, rect):
            self.kill()

class RoboBaddie(GameObject):
    
    main_obj = None
    
    def __init__(self, game, pos):
        if not self.main_obj:
            self.main_obj = pyggel.mesh.OBJ("data/robo.obj", pos=pos, colorize=[0.3, 0.4, 0.5, 1])
        obj = self.main_obj.copy()
        GameObject.__init__(self, game, obj=obj, pos=pos, rotation=0, height=-0.2)
        self.obj.scale = 2.0
        self.scene.add_3d(self.obj)
        self.old_pos = list(self.pos)
        self.hp = 5
        self.hit_timer = 0
        self.obj.colorize = [0.3, 0.4, 0.5, 1]
        self.home_in = False
        
    def update(self):
        self.hit_timer -= 1
        if self.hit_timer > 0:
            self.obj.colorize = [1, 0, 0, 1]
        else:
            self.obj.colorize = [0.3, 0.4, 0.5, 1]
        self.rotate_to(0, self.obj.rotation[1]+3, 0)
        self.move(0.1, (0, 180+self.obj.rotation[1]))
    
    def kill(self):
        if self.alive():
            GameObject.kill(self)
            self.scene.remove_3d(self.obj)
            for i in range(3):
                pos = list(self.obj.pos)
                pos[0] += random.choice([-0.5, -0.4, -0.3, -0.2, -0.1])*random.choice([1, -1])
                pos[1] += random.choice([-0.3, -0.2, -0.1])*random.choice([1, -1])
                pos[2] += random.choice([-0.5, -0.4, -0.3, -0.2, -0.1])*random.choice([1, -1])
                Explosion(self.game, [pos[0], pos[2]], pos[1])
    
    def collide(self, point):
        r = [self.pos[0] - 1.5, self.pos[1] - 1.5, 3.0, 3.0]
        if collidepoint(point, r) and self.hit_timer <= 0:
            self.hit_timer = 4
            self.hp -= 1
            self.game.player.score += 1
            if self.hp <= 0:
                self.kill()
                self.game.player.score += 15
            return 1

    def wall_collide(self, rect):
        #Collide n' slide.
        if collidepoint(self.pos, rect):
            #print [self.pos[0] - self.old_pos[0], self.pos[1] - self.old_pos[1]]
            if self.old_pos[0] >= rect[0]+rect[2] or self.old_pos[0] <= rect[0]:
                self.pos[0] = self.old_pos[0]
            if self.old_pos[1] >= rect[1]+rect[3] or self.old_pos[1] <= rect[1]:
                self.pos[1] = self.old_pos[1]

class Explosion(GameObject):
    
    def __init__(self, game, pos, height):
        GameObject.__init__(self, game, pyggel.image.Image3D("data/explosion.png"), pos=pos, height=height)
        self.scene.add_3d_blend(self.obj)
        self.alpha = 1.0
        self.obj.scale = 0.25
       
    def kill(self):
        if self.alive():
            Object.kill(self)
            self.scene.remove_3d_blend(self.obj)
        
    def update(self):
        self.obj.scale += 0.1
        self.rotate(0, 0, 2)
        self.alpha -= 0.04
        if self.alpha < 0:
            self.kill()
        self.obj.colorize = (1.0, 1.0, 1.0, self.alpha)

class GunFlash(GameObject):
    
    def __init__(self, game, pos):
        GameObject.__init__(self, game, pos=[pos[0], pos[2]], height=pos[1])
        self.obj = pyggel.image.Image3D("data/flash.png", pos=pos)
        self.scene.add_3d_blend(self.obj)
        self.alpha = 1.0
        self.obj.scale = 0.1
       
    def kill(self):
        if self.alive():
            Object.kill(self)
            self.scene.remove_3d_blend(self.obj)
        
    def update(self):
        self.obj.scale += 0.05
        self.alpha -= 0.1
        if self.alpha < 0:
            self.kill()
        self.obj.colorize = (1.0, 1.0, 0.5, self.alpha)

class Wall(Object):
    
    def __init__(self, game, pos):
        Object.__init__(self, self.groups)
        self.pos = pos
