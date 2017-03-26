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
from os.path import expanduser

import mpv


def mpv_wrapper(media, video=True):
    if video:
        player = mpv.MPV(ytdl=True, input_default_bindings=True,
                         input_vo_keyboard=True, ytdl_format=ytdl_format)
    else:
        player = mpv.MPV(ytdl=True, input_default_bindings=True,
                         input_vo_keyboard=True, vid=False,
                         ytdl_format=ytdl_format)
    player.play(media)
    player.wait_for_playback()
    del player


def reattr(stdscr, y, track):
    track = data[start + y - 1]
    invert = 8 if track['highlight'] else 0
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
    stdscr.addstr(0, 0, 'Title')
    stdscr.chgat(0, 0, curses.color_pair(10) | curses.A_BOLD)
    for i, d in enumerate(data2print):
        y = i + 1
        stdscr.addstr(y, 0, d['url'].rjust(curses.COLS - 1))
        stdscr.addstr(y, 0, d['title'][:curses.COLS-12])
        reattr(stdscr, y, data[start + i])
    stdscr.addstr(
        curses.LINES - 2,
        curses.COLS - 16,
        '{:7} {:8}'.format(mode, 'selected' if selected else 'all')
    )
    stdscr.chgat(curses.LINES - 2, 0, curses.color_pair(8))
    stdscr.refresh()


def move(stdscr, data, y, delta):
    global start
    reattr(stdscr, y, data[start + y - 1])
    if start + y + delta < 1:
        start = 0
        reprint(stdscr, data[:curses.LINES-3])
        stdscr.move(1, 0)
        data[0]['highlight'] = True
        reattr(stdscr, 1, data[start])
        data[0]['highlight'] = False
        return 1
    elif start + y + delta > len(data):
        start = len(data) - curses.LINES + 3
        reprint(stdscr, data[-curses.LINES+3:])
        y = curses.LINES - 3
        stdscr.move(y, 0)
        data[-1]['highlight'] = True
        reattr(stdscr, y, data[start + y - 1])
        data[-1]['highlight'] = False
        return y

    if 0 < y + delta < curses.LINES - 2:
        y = y + delta
    elif y + delta < 1:
        start += y + delta - 1
        reprint(stdscr, data[start : start+curses.LINES-3])
        y = 1
    else:
        start += y + delta - curses.LINES + 3
        reprint(stdscr, data[start : start+curses.LINES-3])
        y = curses.LINES - 3
    stdscr.move(y, 0)
    data[start + y - 1]['highlight'] = True
    reattr(stdscr, y, data[start + y - 1])
    data[start + y - 1]['highlight'] = False
    stdscr.refresh()
    return y


parser = ArgumentParser(description="console/curses online media player")
parser.add_argument('-j', '--json-playlist', required=False,
                    help='path to playlist in JSON format')
args = parser.parse_args()

config = ConfigParser()
config.read(expanduser('~/.config/comp/settings.ini'))
ytdl_format = config.get('Init', 'ytdl-format', fallback='best')
mode = config.get('Runtime', 'play-mode', fallback='normal')
selected = config.getboolean('Runtime', 'play-selected-only', fallback=False)
video = config.getboolean('Runtime', 'video', fallback=True)

with open(args.json_playlist) as f:
    data = json.load(f)
for i in data:
    i['error'] = False
    i['playing'] = False
    i['selected'] = False
    i['highlight'] = False


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

# Print initial content
start = 0
reprint(stdscr, data[:curses.LINES-3])
y = 1
data[0]['highlight'] = True
stdscr.move(1, 0)
reattr(stdscr, 1, data[start])
data[0]['highlight'] = False

c = stdscr.getch()
while c != 113:     # letter q
    if c == curses.KEY_RESIZE:
        curses.update_lines_cols()
        reprint(stdscr, data[start : start+curses.LINES-3])
        y = 1
        reattr(stdscr, 1, data[start])
    elif c in (ord('j'), curses.KEY_DOWN):
        y = move(stdscr, data, y, 1)
    elif c in (ord('k'), curses.KEY_UP):
        y = move(stdscr, data, y, -1)
    elif c == curses.KEY_PPAGE:
        y = move(stdscr, data, y, -curses.LINES)
    elif c == curses.KEY_NPAGE:
        y = move(stdscr, data, y, curses.LINES)
    elif c == curses.KEY_HOME:
        y = move(stdscr, data, y, -len(data))
    elif c == curses.KEY_END:
        y = move(stdscr, data, y, len(data))
    elif c == ord(' '):
        data[start + y - 1]['selected'] = not data[start + y - 1]['selected']
        y = move(stdscr, data, y, 1)
    elif c == ord('x'):     # temporally behavior
        mpv_wrapper('https://youtu.be/' + data[start + y - 1]['url'], video)
    stdscr.refresh()
    c = stdscr.getch()

curses.nocbreak()
stdscr.keypad(False)
curses.echo()
curses.endwin()
