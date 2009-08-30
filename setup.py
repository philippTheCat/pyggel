#!/usr/bin/env python
""" Run this with specific commands.
To install simply run from the commandline: python setup.py install
To build a windows installer run: python setup.py bdist_wininst
"""

from distutils.core import setup
import pyggel, os, sys, fnmatch

## Code borrowed from wxPython's setup and config files
## Thanks to Robin Dunn for the suggestion.
## I am not 100% sure what's going on, but it works!
def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)

def find_data_files(srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
    badnames=[".pyc","~"]
    def walk_helper(arg, dirname, files):
        if '.svn' in dirname:
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)
                #if ".pyc" not in filename:
                ## This hairy looking line excludes the filename
                ## if any part of one of  badnames is in it:
                L=len([bad for bad in badnames if bad in filename])
                if L == 0:
                    if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                        names.append(filename)
        if names:
            lst.append( (dirname, names ) )
    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.path.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list

## This is a list of files to install, and where:
## Make sure the MANIFEST.in file points to all the right 
## directories too.
files = find_data_files('examples_and_tutorials/', '*.*')

setup(name='pyggel',
      version=pyggel.get_version(),
      description='PYthon Graphical Game Engine and Libraries',
      author='Matt Roe',
      author_email='RoeBros@gmail.com',
      maintainer='Robert Ramsay',
      maintainer_email='durandal@gmail.com',
      url='http://pyggel.googlecode.com/',
      packages = ['pyggel'],
      data_files = files
      )
