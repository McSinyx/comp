# omp.py - Omni Media Player meta object
# This is a part of comp
#
# comp is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# comp program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with comp.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2017  Nguyễn Gia Phong <vn.mcsinyx@gmail.com>

import json
from collections import deque
from itertools import cycle
from os.path import abspath, expanduser, expandvars, isfile
from random import choice
from time import gmtime, sleep, strftime
from urllib import request

from youtube_dl import YoutubeDL
from mpv import MPV, MpvFormat

DEFAULT_ENTRY = {'filename': '', 'title': '', 'duration': '00:00:00',
                 'error': False, 'playing': False, 'selected': False}
YTDL_OPTS = {'quiet': True, 'default_search': 'ytsearch',
             'extract_flat': 'in_playlist'}


class Omp(object):
    """Omni Media Player meta object.

    Attributes:
        entries (list): list of all tracks
        json_file (str): path to save JSON playlist
        mode (str): the mode to pick and play tracks
        mp (MPV): an mpv instance
        play_backward (bool): flag show if to play the previous track
        play_list (list): list of tracks according to mode
        played (list): list of previously played tracks
        playing (int): index of playing track in played
        playlist (iterator): iterator of tracks according to mode
        search_res (iterator):  title-searched results
        vid (str): flag show if video output is enabled
    """
    def __new__(cls, entries, handler, json_file, mode, mpv_vid, mpv_vo, ytdlf):
        self = super(Comp, cls).__new__(cls)
        self.play_backward, self.reading = False, False
        self.playing = -1
        self.json_file, self.mode, self.vid = json_file, mode, mpv_vid
        self.entries, self.played = entries, []
        self.playlist, self.search_res = iter(()), deque()
        self.mp = MPV(input_default_bindings=True, input_vo_keyboard=True,
                      ytdl=True, ytdl_format=ytdlf)
        return self

    def __init__(self, entries, handler, json_file, mode,
                 mpv_vid, mpv_vo, ytdlf):
        if mpv_vo is not None: self.mp['vo'] = mpv_vo
        self.mp.observe_property('mute', handler)
        self.mp.observe_property('pause', handler)
        self.mp.observe_property('time-pos', handler,
                                 force_fmt=MpvFormat.INT64)

    def __enter__(self): return self

    def update_play_list(self, pick):
        """Update the list of entries to be played."""
        if pick == 'current':
            self.play_list = [self.current()]
        elif pick == 'all':
            self.play_list = deque(self.entries)
            self.play_list.rotate(-self.idx())
        else:
            self.play_list = [i for i in self.entries if i.get('selected')]

    def update_playlist(self):
        """Update the playlist to be used by play function."""
        action, pick = self.mode.split('-')
        self.update_play_list(pick)
        if action == 'play':
            self.playlist = iter(self.play_list)
        elif action == 'repeat':
            self.playlist = cycle(self.play_list)
        else:
            self.playlist = iter(lambda: choice(self.play_list), None)
        if self.playing < -1: self.played = self.played[:self.playing+1]

    def seek(self, amount, reference='relative', precision='default-precise'):
        """Wrap mp.seek with a try clause to avoid crash when nothing is
        being played.
        """
        try:
            self.mp.seek(amount, reference, precision)
        except:
            pass

    def next(self, force=False, backward=False):
        self.play_backward = backward
        if self.mp.idle_active:
            self.play(force)
        else:
            self.seek(100, 'absolute-percent')
            if force: self.mp.pause = False

    def search(self, backward=False):
        """Prompt then search for a pattern."""
        p = re.compile(self.gets('/'), re.IGNORECASE)
        entries = deque(self.entries)
        entries.rotate(-self.idx())
        self.search_res = deque(filter(
            lambda entry: p.search(entry['title']) is not None, entries))
        if backward: self.search_res.reverse()
        if self.search_res:
            self.move(self.idx(self.search_res[0]) - self.idx())
        else:
            self.update_status(_("Pattern not found"), curses.color_pair(1))

    def next_search(self, backward=False):
        """Repeat previous search."""
        if self.search_res:
            self.search_res.rotate(1 if backward else -1)
            self.move(self.idx(self.search_res[0]) - self.idx())
        else:
            self.update_status(_("Pattern not found"), curses.color_pair(1))

    def __exit__(self, exc_type, exc_value, traceback):
        self.mp.quit()
