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
   sudo ./setup.py install --user

Usage
-----

::

   $ comp --help
   usage: comp [-h] [-j JSON_PLAYLIST]
   
   Curses Online Media Player
   
   optional arguments:
     -h, --help            show this help message and exit
     -j JSON_PLAYLIST, --json-playlist JSON_PLAYLIST
                           path to playlist in JSON format
     -y YOUTUBE_PLAYLIST, --youtube-playlist YOUTUBE_PLAYLIST
                        URL to an playlist on Youtube

Keyboard control
^^^^^^^^^^^^^^^^

+--------------+---------------------------------------------+
|     Key      |                   Action                    |
+==============+=============================================+
| Return       | Start playing                               |
+--------------+---------------------------------------------+
| Space        | Toggle pause                                |
+--------------+---------------------------------------------+
| ``A``        | Toggle mute                                 |
+--------------+---------------------------------------------+
| ``V``        | Toggle video                                |
+--------------+---------------------------------------------+
| ``W``        | Save the current playlist under JSON format |
+--------------+---------------------------------------------+
| ``c``        | Select the current track                    |
+--------------+---------------------------------------------+
| ``m``, ``M`` | Cycle through playing modes                 |
+--------------+---------------------------------------------+
| Up, ``k``    | Move a single line up                       |
+--------------+---------------------------------------------+
| Down, ``j``  | Move a single line down                     |
+--------------+---------------------------------------------+
| Left, ``h``  | Seek backward 5 seconds                     |
+--------------+---------------------------------------------+
| Right, ``l`` | Seek forward 5 seconds                      |
+--------------+---------------------------------------------+
| Home         | Move to the beginning of the playlist       |
+--------------+---------------------------------------------+
| End          | Move to the end of the playlist             |
+--------------+---------------------------------------------+
| Page Up      | Move a single page up                       |
+--------------+---------------------------------------------+
| Page Down    | Move a single page down                     |
+--------------+---------------------------------------------+
| F5           | Reprint the screen content                  |
+--------------+---------------------------------------------+

Configuration files
-------------------

The system-wide configuration file is ``/etc/comp/settings.ini``, the
user-specific one is  ``~/.config/mpv/settings.ini``. Default configurations
are listed below::

   [comp]
   # Supported 8 modes: play-current, play-all, play-selected, repeat-current,
   # repeat-all, repeat-selected, shuffle-all and shuffle-selected.
   play-mode = play-current
   
   [mpv]
   # Set if video should be download and play, I only know 2 possible values:
   # auto and no. This can be changed later interactively.
   video = auto
   # Read more on VIDEO OUTPUT DRIVERS section in mpv man page.
   video-output =
   
   [youtube-dl]
   # Read more on FORMAT SELECTION section in youtube-dl man page.
   format = best
