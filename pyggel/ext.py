"""
pyggel.ext
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The ext module contains a large amount of functions for advanced 3d usage.
The layout is not as user friendly or simple as the reset of PYGGEL,
so it is only recommended for advanced users in need of a lot of rendering speed.
"""

def shape_cube(size, pos=(0,0,0), color=(1,1,1,1), hide_faces=[]):
    verts = []
    colors = []
    texcs = []
    norms = []
