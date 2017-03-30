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
from time import gmtime, strftime

from mpv import MPV


def initmpv(ytdl_format, video):
    if video:
        return MPV(input_default_bindings=True, input_vo_keyboard=True,
                   ytdl=True, ytdl_format=ytdl_format)
    else:
        return MPV(input_default_bindings=True, input_vo_keyboard=True,
                   ytdl=True, ytdl_format=ytdl_format, vid=False)


def setno(data, keys):
    """Set all keys of each track in data to False."""
    for key in keys:
        for track in data:
            track[key] = False


def secpair2hhmmss(pos, duration):
    """Quick hack to convert a pair of seconds to HHMMSS / HHMMSS
    string as MPV.get_property_osd_string isn't available.
    """
    if pos is None:
        return ''
    postime, durationtime = gmtime(pos), gmtime(duration)
    # Let's hope media durations are shorter than a day
    timestr = '%M:%S' if duration < 3600 else '%H:%M:%S'
    return '{} / {}'.format(strftime(timestr, postime),
                            strftime(timestr, durationtime))



def updatestatusline(stdscr):
    stdscr.addstr(curses.LINES - 2, 1, '{} {}'.format(
        '|' if mp._get_property('pause', bool) else '>',
        secpair2hhmmss(mp._get_property('time-pos', int),
                       mp._get_property('duration', int))
    ))
    stdscr.addstr(
        curses.LINES - 2,
        curses.COLS - 16,
        '{:7} {:8}'.format(mode, 'selected' if selected else 'all')
    )
    stdscr.chgat(curses.LINES - 2, 0, curses.color_pair(8))
    stdscr.refresh()


def reprint(stdscr, data2print):
    stdscr.clear()
    stdscr.addstr(0, curses.COLS-12, 'URL')
    stdscr.addstr(0, 1, 'Title')
    stdscr.chgat(0, 0, curses.color_pair(10) | curses.A_BOLD)
    for i, track in enumerate(data2print):
        y = i + 1
        stdscr.addstr(y, 0, track['url'].rjust(curses.COLS - 1))
        stdscr.addstr(y, 1, track['title'][:curses.COLS-12])
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
    updatestatusline(stdscr)


def move(stdscr, data, y, delta):
    global start
    if start + y + delta < 1:
        start = 0
        setno(data, ['highlight'])
        data[0]['highlight'] = True
        reprint(stdscr, data[:curses.LINES-3])
        return 1
    elif start + y + delta > len(data):
        start = len(data) - curses.LINES + 3
        y = curses.LINES - 3
        setno(data, ['highlight'])
        data[-1]['highlight'] = True
        reprint(stdscr, data[-curses.LINES+3:])
        return y

    if 0 < y + delta < curses.LINES - 2:
        y = y + delta
    elif y + delta < 1:
        start += y + delta - 1
        y = 1
    else:
        start += y + delta - curses.LINES + 3
        y = curses.LINES - 3
    setno(data, ['highlight'])
    data[start + y - 1]['highlight'] = True
    reprint(stdscr, data[start : start+curses.LINES-3])
    stdscr.refresh()
    return y


parser = ArgumentParser(description="console/curses online media mp")
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
setno(data, ['error', 'playing', 'selected', 'highlight'])

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

mp = initmpv(ytdl_format, video)
mp.observe_property('time-pos', lambda pos: updatestatusline(stdscr))

# Print initial content
start = 0
y = 1
data[0]['highlight'] = True
reprint(stdscr, data[:curses.LINES-3])

# mpv keys: []{}<>.,qQ/*90m-#fTweoPOvjJxzlLVrtsSIdA
# yuighkcbn
c = stdscr.getch()
while c != 113:     # letter q
    if c == curses.KEY_RESIZE:
        curses.update_lines_cols()
        move(stdscr, data, y, 1 - y)
        y = move(stdscr, data, 1, y - 1)
    elif c in (106, curses.KEY_DOWN):   # letter j or down arrow
        y = move(stdscr, data, y, 1)
    elif c in (107, curses.KEY_UP):     # letter k or up arrow
        y = move(stdscr, data, y, -1)
    elif c == curses.KEY_PPAGE:     # page up
        y = move(stdscr, data, y, -curses.LINES)
    elif c == curses.KEY_NPAGE:     # page down
        y = move(stdscr, data, y, curses.LINES)
    elif c == curses.KEY_HOME:  # home
        y = move(stdscr, data, y, -len(data))
    elif c == curses.KEY_END:   # end
        y = move(stdscr, data, y, len(data))
    elif c == 32:   # space
        setno(data, ['playing'])
        mp.play('https://youtu.be/' + data[start + y - 1]['url'])
        data[start + y - 1]['playing'] = True
        reprint(stdscr, data[start : start+curses.LINES-3])
    elif c == 112:  # letter p
        mp._set_property('pause', not mp._get_property('pause', bool), bool)
    elif c == 99:   # letter c
        data[start + y - 1]['selected'] = not data[start + y - 1]['selected']
        y = move(stdscr, data, y, 1)
    c = stdscr.getch()

curses.nocbreak()
stdscr.keypad(False)
curses.echo()
curses.endwin()

del mp
