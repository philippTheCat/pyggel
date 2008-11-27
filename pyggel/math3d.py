"""
pyggle.math3d
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.
"""

import math

def move_with_rotation(pos, rot, amount):
    p=[pos[0],pos[1],pos[2]]
    po=0.0174532925
    p[0] -= math.sin(rot[1]*po)*amount
    p[1] += math.sin(rot[0]*po)*amount
    p[2] += math.cos(rot[1]*po)*amount
    return p

def get_distance(a, b):
    return Vector(a).distance(Vector(b))

class Vector(object):
    ctype = "Vector"
    def __init__(self, pos):
        self.x, self.y, self.z = pos

    def copy(self):
        return Vector((self.x, self.y, self.z))

    def distance(self, other):
        n = self - other
        return math.sqrt(n.x**2 + n.y**2 + n.z**2)

    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def perpendicular(self):
        return self.cross(Vector((-self.y, self.x, self.z)))

    def fast_distance(self, other):
        n = self - other
        return n.x**2 + n.y**2 + n.z**2

    def rotate(self, vec, amount):
        a, b, c = amount

        vec = self - vec

        Sin, Cos, Rad = math.sin, math.cos, math.radians

        if a:
            rad = Rad(-a)
            cos = Cos(rad)
            sin = Sin(rad)

            op = self.copy()

            vec.y = cos * op.y - sin * op.z
            vec.z = sin * op.y + cos * op.z

        if b:
            rad = Rad(-b)
            cos = Cos(rad)
            sin = Sin(rad)

            op = self.copy()

            vec.x = cos * op.x - sin * op.z
            vec.z = sin * op.x + cos * op.z

        if c:
            rad = Rad(-c)
            cos = Cos(rad)
            sin = Sin(rad)

            op = self.copy()

            vec.x = cos * op.x - sin * op.y
            vec.y = sin * op.x + cos * op.y

        return vec + self

    def invert(self):
        return Vector((-self.x, -self.y, -self.z))

    def length(self):
        return self.distance(Vector((0,0,0)))

    def fast_length(self):
        return self.fast_distance(Vector((0,0,0)))

    def normalize(self):
        L = self.length()
        return self / Vector((L, L, L))

    def dot(self, other):
        x = self * other
        return x.x + x.y + x.z

    def get_pos(self):
        return self.x, self.y, self.z

    def set_pos(self, pos):
        self.x, self.y, self.z = pos

    def angle(self, other):
        return math.acos(self.dot(other))

    def __sub__(self, other):
        return Vector((self.x-other.x, self.y-other.y, self.z-other.z))

    def __add__(self, other):
        return Vector((self.x+other.x, self.y+other.y, self.z+other.z))

    __radd__ = __add__

    def __mul__(self, other):
        return Vector((self.x*other.x, self.y*other.y, self.z*other.z))
    __rmul__ = __mul__

    def __div__(self, other):
        x = self.x/other.x if (self.x and other.x) else 0
        y = self.y/other.y if (self.y and other.y) else 0
        z = self.z/other.z if (self.z and other.z) else 0
        return Vector((x, y, z))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return not self == other

    def __nonzero__(self):
        return self != Vector((0,0,0))

    def __iadd__(self, other):
        self.set_pos((self + other).get_pos())

    def __rsub__(self, other):
        return Vector(*(other - self).get_pos())

    def __isub__(self, other):
        self.set_pos((self - other).get_pos())

    def __imul__(self, other):
        self.set_pos((self * other).get_pos())

    def __rdiv__(self, other):
        return Vector((other / self).get_pos())
    def __idiv__(self, other):
        self.set_pos((self / other).get_pos())

    __neg__ = invert

    def __abs__(self):
        return Vector((abs(self.x), abs(self.y), abs(self.z)))

    def __pow__(self, other):
        return Vector((self.x**other.x, self.y**other.y, self.z**other.z))

    def __rpow__(self, other):
        return other ** self

    def cross(self, other):
        return Vector((self.y * other.z - self.z * other.y,
                      self.z * other.x - self.x * other.z,
                      self.x * other.y - self.y * other.x))

    def collide(self, other):
        if other.ctype == "Vector":
            return self == other
        else:
            return other.collide(self)

class Sphere(Vector):
    ctype = "Sphere"
    def __init__(self, pos, radius):
        Vector.__init__(self, pos)
        self.radius = radius

    def collide(self, other):
        if other.ctype == "Vector":
            return other.fast_distance(self) <= self.radius ** 2 #this so we avoid the sqrt call ;)
        elif other.ctype == "Sphere":
            return other.fast_distance(self) <= (self.radius + other.radius) ** 2
        else:
            return other.collide(self)

class AABox(Vector):
    ctype = "AABox"
    def __init__(self, pos, size):
        Vector.__init__(self, pos)

        try:
            self.width, self.height, self.depth = size
        except:
            self.width = self.height = self.depth = size

    def collide(self, other):
        w = self.width * .5
        h = self.height * .5
        d = self.depth * .5

        left = self.x - w
        right = self.x + w
        bottom = self.y - h
        top = self.y + h
        front = self.z - d
        back = self.z + d

        if other.ctype == "Vector":
            return left <= other.x <= right and\
                   bottom <= other.y <= top and\
                   front <= other.z <= back
        elif other.ctype == "Sphere":
            r = other.radius
            return left -r <= other.x <= right + r and\
                   bottom -r <= other.y <= top + r and\
                   front - r <= other.z <= back + r
        elif other.ctype == "AABox":
            points = ((left, bottom, front),
                      (right, bottom, front),
                      (right, top, front),
                      (left, top, front),
                      (left, bottom, back),
                      (right, bottom, back),
                      (right, top, back),
                      (left, top, back))
            for i in points:
                if other.collide(Vector(i)):
                    return True

            #test them against us now...
            w = other.width * .5
            h = other.height * .5
            d = other.depth * .5

            left = other.x - w
            right = other.x + w
            bottom = other.y - h
            top = other.y + h
            front = other.z - d
            back = other.z + d
            points = ((left, bottom, front),
                      (right, bottom, front),
                      (right, top, front),
                      (left, top, front),
                      (left, bottom, back),
                      (right, bottom, back),
                      (right, top, back),
                      (left, top, back))

            for i in points:
                if self.collide(Vector(i)):
                    return True
            return False
        else:
            return other.collide(self)
