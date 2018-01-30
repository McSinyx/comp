# omp.py - Omni Media Player meta object
# This file is part of comp
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
from bisect import bisect_left as bisect
from collections import deque
from gettext import bindtextdomain, gettext as _, textdomain
from itertools import cycle
from os import makedirs
from os.path import abspath, dirname, expanduser, expandvars, isfile
from random import choice
from sys import exc_info
from time import gmtime, sleep, strftime
from urllib import request

from youtube_dl import YoutubeDL
from pkg_resources import resource_filename
from mpv import MPV, MpvFormat

from .ie import JSON_KEYS, extract_info

# Init gettext
bindtextdomain('omp', resource_filename('omp', 'locale'))
textdomain('omp')


def shuffle_init(a):
    """Return in iterator which yield random elements from a,
    and always begin with its first element.
    """
    if a:
        yield a[0]
        while True: yield choice(a)


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

    I/O handlers (defined by front-end):
        print_msg(message, error=False): print a message
        property_handler(name, val): called when a mpv property updated
        read_input(prompt): prompt for user input
        refresh(): update interface content
    """
    def __new__(cls, entries, json_file, mode, mpv_args, ytdlf):
        self = super(Comp, cls).__new__(cls)
        self.play_backward, self.reading = False, False
        self.playing = -1
        self.json_file, self.mode = json_file, mode
        self.entries, self.played = entries, []
        self.playlist, self.search_res = iter(()), deque()
        self.mp = MPV(input_default_bindings=True, input_vo_keyboard=True,
                      ytdl=True, ytdl_format=ytdlf)
        return self

    def __init__(self, entries, json_file, mode, mpv_args, ytdlf):
        for arg, val in mpv_args.items():
            try:
                self.mp[arg] = val
            except:
                self.__exit__(*exc_info())
        @self.mp.property_observer('mute')
        @self.mp.property_observer('pause')
        @self.mp.property_observer('time-pos')
        def observer(name, value): self.property_handler(name, value)
        self.mp.register_key_binding('q', lambda state, key: None)

    def __enter__(self): return self

    def seek(self, amount, reference='relative', precision='default-precise'):
        """Wrap a try clause around mp.seek to avoid crashing when
        nothing is being played.
        """
        try:
            self.mp.seek(amount, reference, precision)
        except:
            self.print_msg(_("Failed to seek"), error=True)

    def add(self, name, value=1):
        """Wrap a try clause around mp.property_add."""
        try:
            self.mp.property_add(name, value)
        except:
            self.print_msg(
                _("Failed to add {} to '{}'").format(value, name), error=True)

    def multiply(self, name, factor):
        """Wrap a try clause around mp.property_multiply."""
        try:
            self.mp.property_multiply(name, factor)
        except:
            self.print_msg(
                _("Failed to multiply '{}' with {}").format(name, value),
                error=True)

    def cycle(self, name, direction='up'):
        """Wrap a try clause around mp.cycle."""
        try:
            self.mp.cycle(name, direction='up')
        except:
            self.print_msg(
                _("Failed to cycle {} '{}'").format(direction, name),
                error=True)

    def idx(self, entry=None):
        """Return the index of the current entry."""
        if entry is None:
            return self.start + self.y - 1
        return self.entries.index(entry)

    def current(self):
        """Return the current entry."""
        try:
            return self.entries[self.idx()]
        except:
            return {}

    def update_playlist(self):
        """Update the playlist to be used by play function."""
        action, pick = self.mode.split('-')
        if pick == 'current':
            self.play_list = deque([self.current()])
        elif pick == 'all':
            self.play_list = deque(self.entries)
            self.play_list.rotate(-self.idx())
        elif pick == 'selected':
            self.play_list = deque([entry for entry in self.entries
                                    if entry.get('selected')])
            indexes = [i for i, entry in enumerate(self.entries)
                       if entry.get('selected')]
            idx = indexes[bisect(indexes, self.idx())]
            self.play_list.rotate(-self.play_list.index(self.entries[idx]))

        if action == 'play':
            self.playlist = iter(self.play_list)
        elif action == 'repeat':
            self.playlist = cycle(self.play_list)
        elif action == 'shuffle':
            self.playlist = shuffle_init(self.play_list)
        if self.playing < -1: self.played = self.played[:self.playing+1]

    def next(self, force=False, backward=False):
        """Go forward/backward in the playlist.

        If forced, this will also unpause the player.
        """
        self.play_backward = backward
        if self.mp.idle_active:
            self.play(force)
        else:
            self.mp.time_pos = self.mp.duration
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

    def dump_json(self):
        """Read user input needed to save the playlist."""
        s = self.read_input(
            _("Save playlist to [{}]: ").format(self.json_file))
        self.json_file = abspath(expanduser(expandvars(s or self.json_file)))
        entries = [{k: v for k, v in entry.items() if k in JSON_KEYS}
                   for entry in self.entries]
        try:
            makedirs(dirname(self.json_file), exist_ok=True)
            with open(self.json_file, 'w') as f:
                json.dump(entries, f, ensure_ascii=False, indent=2,
                          sort_keys=True)
        except:
            errmsg = _("'{}': Can't open file for writing").format(
                self.json_file)
            self.print_msg(errmsg, error=True)
        else:
            self.print_msg(_("'{}' written").format(self.json_file))

    def __exit__(self, exc_type, exc_value, traceback):
        self.mp.quit()
