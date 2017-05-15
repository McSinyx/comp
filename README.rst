=================================
comp - Curses Online Media Player
=================================

This program is a curses front-end for mpv and youtube-dl.

.. image:: https://ipfs.io/ipfs/QmVhz4F53Sym48kXC7vhDMFsfvJ7iL8gaQ1EgoQADJvuAB

Installation
------------

Dependencies
^^^^^^^^^^^^

This program currently only runs on Python 3.5+ on operating systems that the
``curses`` module is supported (i.e. Unix-like OS, e.g. GNU/Linux, macOS and
the BSDs).

It also depends on ``youtube-dl`` and ``libmpv``. Both of those should be
available in your operating system's repository, although it's more
recommended to install ``youtube-dl`` using ``pip`` (currently most distros
still use Python 2 as default so the command is something like ``pip3 install
youtube-dl``).

Installing comp
^^^^^^^^^^^^^^^

I will try to upload the program to PyPI when it's more completed but as of
this moment, I'd suggest you to use ``git`` to get the software::

   git clone https://github.com/McSinyx/comp.git
   cd comp
   sudo ./setup.py install

Usage
-----

Command line arguments
^^^^^^^^^^^^^^^^^^^^^^

::

   $ comp --help
   usage: comp [-h] [-c CONFIG] [--vid {ID,auto,no}] [--vo DRIVER]
               [-f YTDL_FORMAT] [-u URL] [-j JSON_PLAYLIST]

   Curses Online Media Player

   optional arguments:
     -h, --help            show this help message and exit
     -c CONFIG, --config CONFIG
                           location of the configuration file; either the path
                           to the config or its containing directory
     --vid {ID,auto,no}    initial video channel. auto selects the default, no
                           disables video
     --vo DRIVER           specify the video output backend to be used. See
                           VIDEO OUTPUT DRIVERS in mpv(1) man page for details
                           and descriptions of available drivers
     -f YTDL_FORMAT, --format YTDL_FORMAT
                           video format/quality to be passed to youtube-dl
     -u URL, --online-playlist URL
                           URL to an playlist on Youtube
     -j JSON_PLAYLIST, --json JSON_PLAYLIST
                           path to playlist in JSON format. If
                           --online-playlist is already specified, this will be
                           used as the default file to save the playlist

Keyboard control
^^^^^^^^^^^^^^^^

+--------------+---------------------------------------------+
|     Key      |                   Action                    |
+==============+=============================================+
| Return       | Start playing                               |
+--------------+---------------------------------------------+
| Space        | Select the current track                    |
+--------------+---------------------------------------------+
| ``/``, ``?`` | Search forward/backward for a pattern       |
+--------------+---------------------------------------------+
| ``<``, ``>`` | Go forward/backward in the playlist         |
+--------------+---------------------------------------------+
| ``A``        | Toggle mute                                 |
+--------------+---------------------------------------------+
| ``N``        | Repeat previous search in reverse direction |
+--------------+---------------------------------------------+
| ``U``        | Open online playlist                        |
+--------------+---------------------------------------------+
| ``V``        | Toggle video                                |
+--------------+---------------------------------------------+
| ``W``        | Save the current playlist under JSON format |
+--------------+---------------------------------------------+
| ``d``        | Delete current entry                        |
+--------------+---------------------------------------------+
| ``m``, ``M`` | Cycle through playing modes                 |
+--------------+---------------------------------------------+
| ``n``        | Repeat previous search                      |
+--------------+---------------------------------------------+
| ``p``        | Toggle pause                                |
+--------------+---------------------------------------------+
| ``w``        | Download tracks set by playing mode         |
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
| F5           | Redraw the screen content                   |
+--------------+---------------------------------------------+

Configuration files
-------------------

The system-wide configuration file is ``/etc/comp/settings.ini``, the
user-specific one is  ``~/.config/mpv/settings.ini``. Default configurations
are listed below::

   [comp]
   # Initial playing mode, which can be one of these 8 modes: play-current,
   # play-all, play-selected, repeat-current, repeat-all, repeat-selected,
   # shuffle-all and shuffle-selected.
   play-mode = play-current

   [mpv]
   # Initial video channel. auto selects the default, no disables video.
   video = auto
   # Specify the video output backend to be used. See VIDEO OUTPUT DRIVERS in
   # mpv(1) man page for details and descriptions of available drivers.
   video-output =

   [youtube-dl]
   # Video format/quality to be passed to youtube-dl. See FORMAT SELECTION in
   # youtube-dl(1) man page for more details and descriptions.
   format = best
