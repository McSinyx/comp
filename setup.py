#!/usr/bin/env python3

from os import walk
from os.path import join
from sys import prefix

from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='comp',
    version='0.3.1',
    description=('Curses Online Media Player'),
    long_description=long_description,
    url='https://github.com/McSinyx/comp',
    author='Nguyễn Gia Phong',
    author_email='vn.mcsinyx@gmail.com',
    license='AGPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console :: Curses',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Natural Language :: Vietnamese',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'Topic :: Multimedia :: Video :: Display'
    ],
    keywords='youtube-dl mpv-wrapper curses console-application multimedia',
    install_requires=['python-mpv', 'youtube-dl'],
    data_files=[
        *((join(prefix, 'share', i[0]), [join(i[0], 'comp.mo')])
          for i in walk('locale') if i[2]),
        ('/etc/comp', ['settings.ini'])
    ],
    py_modules=['omp'],
    scripts=['comp'],
    platforms=['POSIX']
)
