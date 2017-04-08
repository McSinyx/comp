#!/usr/bin/env python3

from distutils.core import setup
from sys import prefix

with open('README.rst') as f:
    long_description = f.read()

setup(name='comp', version='0.1.1a3',
      url='https://github.com/McSinyx/comp',
      description=('Curses Online Media Player'),
      long_description=long_description,
      author='Nguyễn Gia Phong', author_email='vn.mcsinyx@gmail.com',
      py_modules=['mpv'], scripts=['comp'],
      data_files=[
          ('{}/share/locale/vi/LC_MESSAGES/'.format(prefix), ['locale/vi/LC_MESSAGES/comp.mo']),
          ('/etc/comp', ['settings.ini'])
      ], classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console :: Curses',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Natural Language :: English',
          'Natural Language :: Vietnamese',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.5',
          'Topic :: Multimedia :: Sound/Audio :: Players',
          'Topic :: Multimedia :: Video :: Display'
      ], platforms=['POSIX'], license='AGPLv3')
