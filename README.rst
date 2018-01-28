===============================
comp - Curses Omni Media Player
===============================

**comp** is a `mpv <https://mpv.io/>`_ front-end using curses. It has basic
media player functions and can to extract playlists from multiple sources such
as media sites supported by `youtube-dl <https://rg3.github.io/youtube-dl/>`_,
local and direct URL to video/audio and its own JSON playlist format.

.. image:: https://github.com/McSinyx/comp/raw/master/doc/screenshot.png

Installation
------------

**comp** requires Python 3.5+ with ``curses`` module (only available on
Unix-like OSes such as GNU/Linux and the BSDs) and ``libmpv`` (available as
``libmpv1`` in Debian/Ubuntu, openSUSE; and as ``mpv`` in Arch Linux, Gentoo,
macOS Homebrew repository). It also depends on ``python-mpv`` and
``youtube-dl`` but the setup program will automatically install them if they
are missing.

As ``setuptools`` will `install in an egg and cause breakage
<https://github.com/McSinyx/comp/issues/5>`_, using ``pip`` (Python 3 version) 
is a must.  After `installing it <https://pip.pypa.io/en/latest/installing/>`_,
run ``pip3 install comp`` (you might want to add ``--user`` flag to use the
`User Scheme <https://pip.pypa.io/en/stable/user_guide/#user-installs>`_).

For developers, clone the `Github repo <https://github.com/McSinyx/comp>`_ then
simply run the ``comp`` executable to test the program. If you insist on
installing it, still use ``pip3``: ``pip3 install .``. Note that **comp** is
distibuted in a ``wheel`` created via ``./setup.py bdist_wheel``.

Command line options
--------------------

::

   usage: comp [-h] [-v] [-e {json,mpv,youtube-dl}] [-c CONFIG] [--vid VID]
               [--vo DRIVER] [-f YTDL_FORMAT]
               playlist

   Curses Omni Media Player

   positional arguments:
     playlist              path or URL to the playlist

   optional arguments:
     -h, --help            show this help message and exit
     -v, --version         show program's version number and exit
     -e {json,mpv,youtube-dl}, --extractor {json,mpv,youtube-dl}
                           playlist extractor, default is youtube-dl
     -c CONFIG, --config CONFIG
                           path to the configuration file
     --vid VID             initial video channel. auto selects the default, no
                           disables video
     --vo DRIVER           specify the video output backend to be used. See
                           VIDEO OUTPUT DRIVERS in mpv(1) for details and
                           descriptions of available drivers
     -f YTDL_FORMAT, --format YTDL_FORMAT
                           video format/quality to be passed to youtube-dl

Examples
^^^^^^^^

Open a JSON playlist::

   comp -e json test/playlist.json

Open a Youtube playlist with video height lower than 720::

   comp -f '[height<720]' https://www.youtube.com/watch?list=PLnk14Iku8QM7R3ARnrj1TwYSZleF-i7jT

Keyboard control
----------------

Bindings inherited from mpv
^^^^^^^^^^^^^^^^^^^^^^^^^^^

For convenience purpose, I try to mimic **mpv** default keybindings, but many
are slightly different from **mpv** exact behaviour (mainly because of the lack
of keys which are unsupported by ``curses``). So I will list all of them here
for you to `compare <https://github.com/mpv-player/mpv/blob/master/DOCS/man/mpv.rst#keyboard-control>`_:

Left and Right
   Seek backward/forward 5 seconds. Shifted arrow does a 1 second seek.

Up and Down
   Seek backward/forward 1 minute.

``[`` and ``]``
   Decrease/increase current playback speed by 10%.

``{`` and ``}``
   Halve/double current playback speed.

Backspace
   Reset playback speed to normal.

``<`` and ``>``
   Go backward/forward in the playlist.

Return
   Start playing.

Space / ``p``
   Pause (pressing again unpauses).

``.``
   Step forward. Pressing once will pause, every consecutive press will play
   one frame and then go into pause mode again.

``,``
   Step backward. Pressing once will pause, every consecutive press will play
   one frame in reverse and then go into pause mode again.

``q``
   Stop playing and quit.

``/`` / ``9`` and ``*`` / ``0``
   Decrease/increase volume.

``m``
   Mute sound.

``_``
   Cycle through the available video tracks.

``#``
   Cycle through the available audio tracks.

``f``
   Toggle fullscreen.

``T``
   Toggle stay-on-top.

``w`` and ``e``
   Decrease/increase pan-and-scan range.

``o`` / ``P``
   Show progression bar, elapsed time and total duration on the OSD.

``O``
   Toggle OSD states between normal and playback time/duration.

``v``
   Toggle subtitle visibility.

``j`` and ``J``
   Cycle through the available subtitles.

``x`` and ``z``
   Adjust subtitle delay by +/- 0.1 seconds.

``l``
   Set/clear A-B loop points.

``L``
   Toggle infinite looping.

Ctrl-``+`` and Ctrl-``-``
   Adjust audio delay (A/V sync) by +/- 0.1 seconds.

``u``
   Switch between applying no style overrides to SSA/ASS subtitles, and
   overriding them almost completely with the normal subtitle style.

``V``
   Toggle subtitle VSFilter aspect compatibility mode.

``r`` and ``t``
   Move subtitles up/down.

``s``
   Take a screenshot.

``S``
   Take a screenshot, without subtitles.

Alt-``s``
   Take a screenshot each frame.

Page Up and Page Down
   Seek to the beginning of the previous/next chapter.

``d``
   Activate/deactivate deinterlacer.

``A``
   Cycle aspect ratio override.

``1`` and ``2``
   Adjust contrast.

``3`` and ``4``
   Adjust brightness.

``5`` and ``6``
   Adjust gamma.

``7`` and ``8``
   Adjust saturation.

Alt-``0``
   Resize video window to half its original size.

Alt-``1``
   Resize video window to its original size.

Alt-``2``
   Resize video window to double its original size.

``E``
   Cycle through editions.

Movements and selections
^^^^^^^^^^^^^^^^^^^^^^^^

The following keybindings are Emacs-like since most characters are taken by
**mpv**.

Ctrl-``p`` and Ctrl-``n``
   Move a single line up/down.

Alt-``v`` and Ctrl-``v``
   Move a single page up/down.

Home / Ctrl-``<`` and End / Ctrl-``>``
   Move to the beginning/end of the playlist.

Ctrl-Space
   Deselect/reselect the current entry and move down a line.

Playlist manipulation
^^^^^^^^^^^^^^^^^^^^^

Ctrl-``o``
   Open playlist.

Ctrl-``i``
   Insert playlist.

Ctrl-``f`` and Alt-``f``
   Search forward/backward for a pattern.

Alt-``m``
   Cycle through playing modes.

Delete
   Delete the current entry.

``W``
   Save the current playlist under JSON format.

F5
   Redraw the screen content.

``:``
   Execute a **mpv** command.

Configuration files
-------------------

If not specified by the ``--config``, (user-specific) configuration file is
``~/.config/mpv/settings.ini``. Default configurations
are listed below::

   [comp]
   # Initial playing mode, which can be one of these 8 modes: play-current,
   # play-all, play-selected, repeat-current, repeat-all, repeat-selected,
   # shuffle-all and shuffle-selected.
   play-mode = play-current

   [mpv]
   # Options to be parsed to mpv. See OPTIONS section on mpv(1) man pages for
   # its complete list of available options.
   # For example:
   #vo = xv
   #ontop = yes
   #border = no
   #force-window = yes
   #autofit = 500x280
   #geometry = -15-50

   [youtube-dl]
   # Video format/quality to be passed to youtube-dl. See FORMAT SELECTION in
   # youtube-dl(1) man page for more details and descriptions.
   format = best


Bugs
----

Media durations are not extracted from online playlists as
``youtube-dl.YoutubeDL`` option ``extract_flat`` is set to ``'in_playlist'``.
This is rather a feature to save up bandwidth than a bug because a track's
duration is updated when it's played.
