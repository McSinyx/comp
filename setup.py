#!/usr/bin/env python3

from distutils.core import setup

with open('README.rst') as f:
    long_description = f.read()

setup(name = 'comp',
      version = '0.1.0a1',
      url = 'https://github.com/McSinyx/comp',
      description = ('Curses Online Media Player'),
      long_description=long_description,
      author = 'McSinyx',
      author_email = 'vn.mcsinyx@gmail.com',
      py_modules = ['mpv'],
      scripts=['comp.py'],
      classifiers = ['Development Status :: 1 - Planning',
                     'Environment :: Console :: Curses',
                     'Intended Audience :: End Users/Desktop',
                     'Natural Language :: English',
                     'Natural Language :: Vietnamese',  # planned
                     'Operating System :: POSIX',
                     'Programming Language :: Python :: 3.5',
                     'Topic :: Multimedia :: Sound/Audio :: Players',
                     'Topic :: Multimedia :: Video :: Display'],
      license = 'AGPLv2'
)
