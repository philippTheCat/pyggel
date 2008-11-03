import math

def move_with_rotation(pos, rot, amount):
    p=[pos[0],pos[1],pos[2]]
    po=0.0174532925
    p[0] -= math.sin(rot[1]*po)*amount
    p[1] += math.sin(rot[0]*po)*amount
    p[2] += math.cos(rot[1]*po)*amount
    return p

def sub_vector(v1, v2):
    v=[]
    for i in range(len(v1)):
        v.append(v1[i]-v2[i])
    return v

def get_distance(v1, v2):
    a, b, c = sub_vector(v1, v2)
    return math.sqrt(a**2+b**2+c**2)
