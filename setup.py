#!/usr/bin/env python3

from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='comp',
    version='0.3.6',
    description=('Curses Omni Media Player'),
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
        'Topic :: Multimedia :: Video :: Display'],
    keywords='youtube-dl mpv-wrapper curses console-application multimedia',
    packages=['omp'],
    install_requires=['python-mpv', 'youtube-dl'],
    python_requires='>=3.5',
    package_data={'omp': ['locale/*/LC_MESSAGES/omp.mo']},
    data_files=[('share/man/man1', ['doc/comp.1'])],
    scripts=['comp'],
    platforms=['POSIX'])
