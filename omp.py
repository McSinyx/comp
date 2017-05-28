# omp.py - comp library for playing and playlist management
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
from os.path import abspath, expanduser, expandvars, isfile
from requests import head
from time import gmtime, sleep, strftime

from youtube_dl import YoutubeDL
from mpv import MPV, MpvFormat

DEFAULT_ENTRY = {'filename': '', 'title': '', 'duration': '00:00:00',
                 'error': False, 'playing': False, 'selected': False}
YTDL_OPTS = {'quiet': True, 'default_search': 'ytsearch',
             'extract_flat': 'in_playlist'}


def extract_info(filename, extractor='youtube-dl'):
    """Return list of entries extracted from a path or URL using
    specified extractor.

    The extractor could be either 'json', 'mpv' or 'youtube-dl'. If is
    not one of them or not specified, youtube-dl will be used.
    """

    def json_extract_info(filename):
        try:
            with open(filename) as f: raw_info = json.load(f)
            info = []
            for i in raw_info:
                e = DEFAULT_ENTRY.copy()
                for k in e:
                    if k in i and isinstance(i[k], type(e[k])): e[k] = i[k]
                info.append(e)
        except:
            return []
        else:
            return info

    def mpv_extract_info(filename):
        mp = MPV(ytdl=True)
        mp.play(filename)
        while mp.duration is None:
            sleep(0.25)
            if mp.playback_abort: return []
        info = {'filename': filename, 'title': mp.media_title.decode(),
                'duration': mp.osd.duration, 'error': False, 'playing': False,
                'selected': False}
        mp.quit()
        return [info]

    def ytdl_extract_info(filename):
        with YoutubeDL(YTDL_OPTS) as ytdl:
            raw_info = ytdl.extract_info(filename, download=False)
            info = raw_info.get('entries', [raw_info])
            for i in info:
                if 'webpage_url' in i:
                    i['filename'] = i['webpage_url']
                elif (i['ie_key'] == 'Youtube'
                      or i['extractor'] == 'youtube'):
                    i['filename'] = 'https://youtu.be/' + i['id']
                else:
                    i['filename'] = i['url']
                if 'title' not in i:
                    i['title'] = ytdl.extract_info(i['filename'],
                                                   download=False)['title']
                if 'duration' not in i:
                    i['duration'] = '00:00:00'
                elif isinstance(i['duration'], int):
                    i['duration'] = strftime('%H:%M:%S', gmtime(i['duration']))
                for k in 'error', 'playing', 'selected': i.setdefault(k, False)
                for k in i.copy():
                    if k not in DEFAULT_ENTRY: i.pop(k)
        return info

    try:
        if (extractor != 'youtube-dl' and head(filename).status_code >= 400
            and isfile(expanduser(expandvars(filename)))):
            filename = abspath(expanduser(expandvars(filename)))
    except:
        pass
    if extractor == 'json':
        return json_extract_info(filename)
    elif extractor == 'mpv':
        return mpv_extract_info(filename)
    else:
        return ytdl_extract_info(filename)


class Omp(object):
    """Meta object for playing and playlist management.

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
    def __new__(cls, entries, handler, json_file, mode, mpv_vo, mpv_vid, ytdlf):
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
                 mpv_vo, mpv_vid, ytdlf):
        if mpv_vo is not None: self.mp['vo'] = mpv_vo
        self.mp.observe_property('mute', handler)
        self.mp.observe_property('pause', handler)
        self.mp.observe_property('time-pos', handler,
                                 force_fmt=MpvFormat.INT64)

    def __enter__(self): return self

    def play(self, force=False):
        """Play the next track."""
        def mpv_play(entry, force):
            self.setno('playing')
            entry['playing'] = True
            self.mp.vid = self.vid
            try:
                self.mp.play(self.getlink(entry))
            except:
                entry['error'] = True
            self.print(entry)
            if force: self.mp.pause = False
            self.mp.wait_for_playback()
            self.play()
            entry['playing'] = False
            self.print(entry)

        if self.play_backward and -self.playing < len(self.played):
            self.playing -= 1
            t = self.played[self.playing], force
        elif self.playing < -1:
            self.playing += 1
            t = self.played[self.playing], force
        else:
            try:
                self.played.append(next(self.playlist))
            except StopIteration:
                return
            else:
                t = self.played[-1], force

        self.play_backward = False
        play_thread = Thread(target=mpv_play, args=t, daemon=True)
        play_thread.start()

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
        comp.play_backward = backward
        if self.mp.idle_active:
            self.play(force)
        else:
            self.seek(100, 'absolute-percent')
            if force: self.mp.pause = False

    def download(self):
        with YoutubeDL({'quiet': True}) as ytdl:
            ytdl.download([self.getlink(i) for i in self.play_list])

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


if __name__ == '__main__':
    print(extract_info('gplv3.ogg', 'mpv'))
    print(extract_info('http://www.youtube.com/watch?v=VmOiDst8Veg', 'mpv'))
    print(extract_info('http://www.youtube.com/watch?v=VmOiDst8Veg', 'youtube-dl'))
    print(extract_info('https://www.youtube.com/watch?list=PLFgquLnL59akuvsCHG83KKO2dpMA8uJQl', 'youtube-dl'))
    print(extract_info('foo.json', 'json'))
