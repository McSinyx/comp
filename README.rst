=================================
comp - Curses Online Media Player
=================================

This program is a curses front-end for mpv and youtube-dl.

Installation
------------

Dependencies
^^^^^^^^^^^^

This program currently only runs on Python 3.5+ on operating systems that the
``curses`` module is supported (i.e. Unix-like OS, e.g. GNU/Linux, macOS and
the BSDs).

It also depends on ``youtube-dl`` and ``libmpv``. Both of those should be
available in your operating system's repository. 

Installing comp
^^^^^^^^^^^^^^^

I will try to upload the program to PyPI when it's more completed but as of
this moment, I'd suggest you to use ``git`` to get the software::

   git clone https://github.com/McSinyx/comp.git
   cd comp
   ./setup.py install --user

Usage
-----

Command line arguments::

   $ comp -h
   usage: comp [-h] [-j JSON_PLAYLIST]
   
   console/curses online media mp
   
   optional arguments:
     -h, --help            show this help message and exit
     -j JSON_PLAYLIST, --json-playlist JSON_PLAYLIST
                           path to playlist in JSON format

Keyboard control
^^^^^^^^^^^^^^^^

+--------------+-------------------------------+
|     Key      |            Action             |
+==============+===============================+
| ``h``, Up    | Move a single line up         |
+--------------+-------------------------------+
| ``j``, Down  | Move a single line down       |
+--------------+-------------------------------+
| Page Up      | Move a single page up         |
+--------------+-------------------------------+
| Page Down    | Move a single page down       |
+--------------+-------------------------------+
| Home         | Move to the begin of the list |
+--------------+-------------------------------+
| End          | Move to the end of the list   |
+--------------+-------------------------------+
| ``c``        | Select the current track      |
+--------------+-------------------------------+
| ``p``        | Start playing                 |
+--------------+-------------------------------+
| Space        | Toggle pause                  |
+--------------+-------------------------------+
| ``m``, ``M`` | Cycle through playing modes   |
+--------------+-------------------------------+
| ``A``        | Toggle mute                   |
+--------------+-------------------------------+
| ``V``        | Toggle video                  |
+--------------+-------------------------------+

Configurations
--------------

``comp`` uses INI format for its config file, placed in
``~/.config/comp/settings.ini``::

   [comp]
   # Supported 8 modes: play-current, play-all, play-selected, repeat-current,
   # repeat-all, repeat-selected, shuffle-all and shuffle-selected
   play-mode = shuffle-selected
   
   [mpv]
   # Set if video should be download and play, I only know 2 possible values:
   # auto and no. This can be changed later interactively.
   video = no
   # Read more on VIDEO OUTPUT DRIVERS section in mpv man page
   video-output = xv
   
   [youtube-dl]
   # Read more on youtube-dl man page
   format = best
