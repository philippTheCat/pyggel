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
    def __init__(self, pos):
        self.x, self.y, self.z = pos

    def copy(self):
        return Vector(self.x, self.y, self.z)

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
        return self / Vector(L, L, L)

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
        return Vector(x, y, z)

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
        return Vector(abs(self.x), abs(self.y), abs(self.z))

    def __pow__(self, other):
        return Vector((self.x**other.x, self.y**other.y, self.z**other.z))

    def __rpow__(self, other):
        return other ** self

    def cross(self, other):
        return Vector(self.y * other.z - self.z * other.y,
                      self.z * other.x - self.x * other.z,
                      self.x * other.y - self.y * other.x)

class Projection(object):
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def intersects(self, other):
        return self.max > other.min and other.max > self.min

class Polygon(object):
    def __init__(self, points):
        if isinstance(points[0], Vector):
            self.points = points
        else:
            self.points = []
            for i in points:
                self.points.append(Vector(i))

        self.edges = []
        L = len(self.points)
        for i in xrange(L):
            p = self.points[i]
            next = self.points[(i+1)%L]
            self.edges.append(next - p)

    def project_to_axis(self, axis):
        projected_points = []
        for point in self.points:
            projected_points.append(point.dot(axis))
        return Projection(min(projected_points), max(projected_points))

    def collidepoly(self, other):
        try:
            edges = self.edges + other.edges

            for e in edges:
                axis = e.normalize().perpendicular()

                self_ = self.project_to_axis(axis)
                other = other.project_to_axis(axis)

                if not self_.intersects(other):
                    return False
            return True
        except:
            return True
            
