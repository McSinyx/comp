#!/usr/bin/env python3
 
# comp - Curses Online Media Player
# Copyright (C) 2017  Raphael McSinyx
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import curses
import json
from argparse import ArgumentParser
from configparser import ConfigParser
from itertools import cycle
from os.path import expanduser
from random import choice
from time import gmtime, strftime
from threading import Thread

from mpv import MPV

MODES = ('play-current', 'play-all', 'play-selected', 'repeat-current',
         'repeat-all', 'repeat-selected', 'shuffle-all', 'shuffle-selected')


def setno(data, keys):
    """Set all keys of each track in data to False."""
    for key in keys:
        for track in data:
            track[key] = False


def playlist(mode):
    """Return a generator of tracks to be played."""
    action, choose_from = mode.split('-')
    if choose_from == 'all': tracks = data
    else: tracks = [track for track in data if track[choose_from]]
    # Somehow yield have to be used instead of returning a generator
    if action == 'play':
        for track in tracks: yield track
    elif action == 'repeat':
        for track in cycle(tracks): yield track
    elif tracks:
        while True: yield choice(tracks)


def play():
    for track in playlist(mode):
        setno(data, ['playing'])
        data[data.index(track)]['playing'] = True
        reprint(stdscr, data[start : start+curses.LINES-3])
        mp.play('https://youtu.be/' + track['url'])
        mp.wait_for_playback()


def secpair2hhmmss(pos, duration):
    """Quick hack to convert a pair of seconds to HHMMSS / HHMMSS
    string as MPV.get_property_osd_string isn't available.
    """
    if pos is None: return ''
    postime, durationtime = gmtime(pos), gmtime(duration)
    # Let's hope media durations are shorter than a day
    timestr = '%M:%S' if duration < 3600 else '%H:%M:%S'
    return '{} / {}'.format(strftime(timestr, postime),
                            strftime(timestr, durationtime))


def update_status_line(stdscr, mp):
    left = ' ' + secpair2hhmmss(mp._get_property('time-pos', int),
                                mp._get_property('duration', int))
    right = ' {} {}{} '.format(mode,
                               ' ' if mp._get_property('mute', bool) else 'A',
                               ' ' if mp._get_property('vid') == 'no' else 'V')
    if left != ' ':
        left += ' | ' if mp._get_property('pause', bool) else ' > '
        stdscr.addstr(curses.LINES - 2, 0, left, curses.color_pair(8))
        title_len = curses.COLS - len(left + right)
        center = mp._get_property('media-title').ljust(title_len)[:title_len]
        stdscr.addstr(curses.LINES - 2, len(left), center,
                      curses.color_pair(8) | curses.A_BOLD)
        stdscr.addstr(curses.LINES - 2, len(left + center), right,
                      curses.color_pair(8))
    else:
        stdscr.addstr(curses.LINES - 2, 0, right.rjust(curses.COLS),
                      curses.color_pair(8))
    stdscr.refresh()


def reattr(stdscr, y, track):
    invert = 8 if track['current'] else 0
    if track['error']:
        stdscr.chgat(y, 0, curses.color_pair(1 + invert) | curses.A_BOLD)
    elif track['playing']:
        stdscr.chgat(y, 0, curses.color_pair(3 + invert) | curses.A_BOLD)
    elif track['selected']:
        stdscr.chgat(y, 0, curses.color_pair(5 + invert) | curses.A_BOLD)
    elif invert:
        stdscr.chgat(y, 0, curses.color_pair(12) | curses.A_BOLD)
    else:
        stdscr.chgat(y, 0, curses.color_pair(0) | curses.A_NORMAL)


def reprint(stdscr, data2print):
    stdscr.clear()
    stdscr.addstr(0, curses.COLS-12, 'URL')
    stdscr.addstr(0, 1, 'Title')
    stdscr.chgat(0, 0, curses.color_pair(10) | curses.A_BOLD)
    for i, track in enumerate(data2print):
        y = i + 1
        stdscr.addstr(y, 0, track['url'].rjust(curses.COLS - 1))
        stdscr.addstr(y, 1, track['title'][:curses.COLS-14])
        reattr(stdscr, y, track)
    update_status_line(stdscr, mp)


def move(stdscr, data, y, delta):
    global start
    if start + y + delta < 1:
        if start + y == 1:
            return 1
        start = 0
        setno(data, ['current'])
        data[0]['current'] = True
        reprint(stdscr, data[:curses.LINES-3])
        return 1
    elif start + y + delta > len(data):
        if start + y == len(data):
            return curses.LINES - 3
        start = len(data) - curses.LINES + 3
        y = curses.LINES - 3
        setno(data, ['current'])
        data[-1]['current'] = True
        reprint(stdscr, data[-curses.LINES+3:])
        return y

    if y + delta < 1:
        start += y + delta - 1
        y = 1
        setno(data, ['current'])
        data[start]['current'] = True
        reprint(stdscr, data[start : start+curses.LINES-3])
    elif y + delta > curses.LINES - 3:
        start += y + delta - curses.LINES + 3
        y = curses.LINES - 3
        setno(data, ['current'])
        data[start + curses.LINES - 4]['current'] = True
        reprint(stdscr, data[start : start+curses.LINES-3])
    else:
        data[start + y - 1]['current'] = False
        reattr(stdscr, y, data[start + y - 1])
        y = y + delta
        data[start + y - 1]['current'] = True
        reattr(stdscr, y, data[start + y - 1])
        stdscr.refresh()
    return y


parser = ArgumentParser(description="console/curses online media mp")
parser.add_argument('-j', '--json-playlist', required=False,
                    help='path to playlist in JSON format')
args = parser.parse_args()

config = ConfigParser()
config.read(expanduser('~/.config/comp/settings.ini'))
mode = config.get('comp', 'play-mode', fallback='play-all')
video = config.get('mpv', 'video', fallback='auto')
video_output = config.get('mpv', 'video-output', fallback='')
ytdlf = config.get('youtube-dl', 'format', fallback='best')

with open(args.json_playlist) as f:
    data = json.load(f)
setno(data, ['error', 'playing', 'selected', 'current'])

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(True)
curses.curs_set(False)
curses.start_color()
curses.use_default_colors()
curses.init_pair(1, 1, -1)
curses.init_pair(2, 2, -1)
curses.init_pair(3, 3, -1)
curses.init_pair(4, 4, -1)
curses.init_pair(5, 5, -1)
curses.init_pair(6, 6, -1)
curses.init_pair(7, 7, -1)
curses.init_pair(8, -1, 7)
curses.init_pair(9, -1, 1)
curses.init_pair(10, -1, 2)
curses.init_pair(11, -1, 3)
curses.init_pair(12, -1, 4)
curses.init_pair(13, -1, 5)
curses.init_pair(14, -1, 6)

mp = MPV(input_default_bindings=True, input_vo_keyboard=True,
         ytdl=True, ytdl_format=ytdlf)
if video_output: mp['vo'] = video_output
mp._set_property('vid', video)
mp.observe_property('mute', lambda foo: update_status_line(stdscr, mp))
mp.observe_property('pause', lambda foo: update_status_line(stdscr, mp))
mp.observe_property('time-pos', lambda foo: update_status_line(stdscr, mp))
mp.observe_property('vid', lambda foo: update_status_line(stdscr, mp))

# Print initial content
start = 0
y = 1
data[0]['current'] = True
reprint(stdscr, data[:curses.LINES-3])

# mpv keys: []{}<>.,qQ/*90m-#fTweoPOvjJxzlLVrtsSIdA
# yuighkcbn
c = stdscr.getch()
while c != 113:     # letter q
    if c == curses.KEY_RESIZE:
        curses.update_lines_cols()
        start += y - 1
        y = 1
        reprint(stdscr, data[start : start+curses.LINES-3])
    elif c in (106, curses.KEY_DOWN):   # letter j or down arrow
        y = move(stdscr, data, y, 1)
    elif c in (107, curses.KEY_UP):     # letter k or up arrow
        y = move(stdscr, data, y, -1)
    elif c == curses.KEY_PPAGE:     # page up
        y = move(stdscr, data, y, 4 - curses.LINES)
    elif c == curses.KEY_NPAGE:     # page down
        y = move(stdscr, data, y, curses.LINES - 4)
    elif c == curses.KEY_HOME:  # home
        y = move(stdscr, data, y, -len(data))
    elif c == curses.KEY_END:   # end
        y = move(stdscr, data, y, len(data))
    elif c == 109:  # letter m
        mode = MODES[(MODES.index(mode) + 1) % 8]
        update_status_line(stdscr, mp)
    elif c == 77:   # letter M
        mode = MODES[(MODES.index(mode) - 1) % 8]
        update_status_line(stdscr, mp)
    elif c == 112:  # letter p
        mp._set_property('pause', False, bool)
        play_thread = Thread(target=play)
        play_thread.daemon = True
        play_thread.start()
    elif c == 32:   # space
        mp._set_property('pause', not mp._get_property('pause', bool), bool)
    elif c == 99:   # letter c
        data[start + y - 1]['selected'] = not data[start + y - 1]['selected']
        y = move(stdscr, data, y, 1)
    elif c == 97:   # letter a
        mp._set_property('mute', not mp._get_property('mute', bool), bool)
    elif c == 118:  # letter v
        mp._set_property('vid', 'auto' if mp._get_property('vid') == 'no' else 'no')
    c = stdscr.getch()

curses.nocbreak()
stdscr.keypad(False)
curses.echo()
curses.endwin()

del mp
