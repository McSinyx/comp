#!/usr/bin/env python3

from distutils.core import setup

with open('README.rst') as f:
    long_description = f.read()

setup(name = 'comp',
      version = '0.1.0a1',
      url = 'https://github.com/McSinyx/comp',
      description = ('console/curses online media player'),
      long_description=long_description,
      author = 'McSinyx',
      author_email = 'vn.mcsinyx@gmail.com',
      license = 'AGPLv2',
      py_modules = ['mpv'],
      scripts=['comp']
)
