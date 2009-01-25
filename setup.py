#!/usr/bin/env python
from distutils.core import setup
setup(name='pyggel',
      version='0.1.a',
      description='PYthon Graphical Game Engine and Libraries',
      author='Matt Roe',
      author_email='RoeBros@gmail.com',
      maintainer='Robert Ramsay',
      maintainer_email='durandal@gmail.com',
      url='http://pyggel.googlecode.com/',
      packages = ['pyggel'],
      py_modules=['camera', 'data', 'font', 'geometry', 'image', 'include',
                  'light', 'math3d', 'mesh', 'misc', 'particle', 'picker',
                  'scene', 'view'],
      #TODO: the demos and 3d files
      #data_files=[('data', ['data/*.png']),
      #            ('data', ['data/*.obj']),
      #            ('data', ['data/*.mtl']),]
      )
