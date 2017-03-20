#!/usr/bin/env python3

import curses
import json
from argparse import ArgumentParser

import mpv


def mpv_wrapper(media, video=True):
    if video:
        player = mpv.MPV(ytdl=True, input_default_bindings=True,
                         input_vo_keyboard=True)
    else:
        player = mpv.MPV(ytdl=True, input_default_bindings=True,
                         input_vo_keyboard=True, vid=False)
    player.register_key_binding('b', player.quit_watch_later)
    player.play(media)
    player.wait_for_playback()
    del player


def interface(stdscr):
    def reattr(y, highlight=False):
        if DATA[start + y - 1]['selected'] and highlight:
            stdscr.chgat(y, 0, curses.color_pair(11) | curses.A_BOLD)
        elif DATA[start + y - 1]['selected']:
            stdscr.chgat(y, 0, curses.color_pair(3) | curses.A_BOLD)
        elif highlight:
            stdscr.chgat(y, 0, curses.color_pair(12) | curses.A_BOLD)
        else:
            stdscr.chgat(y, 0, curses.color_pair(0) | curses.A_NORMAL)

    def reprint():
        stdscr.addstr(0, curses.COLS-12, 'URL')
        stdscr.addstr(0, 0, 'Title')
        stdscr.chgat(0, 0, curses.color_pair(10) | curses.A_BOLD)
        for i, d in enumerate(DATA[start : start+curses.LINES-1]):
            stdscr.addstr(i + 1, 0, d['url'].rjust(curses.COLS - 1))
            stdscr.addstr(i + 1, 0, d['title'][:curses.COLS-12])
            reattr(i + 1)
        stdscr.refresh()

    def move(y, delta):
        nonlocal start
        reattr(y)
        if start + y + delta < 1:
            start = 0
            reprint()
            stdscr.move(1, 0)
            reattr(1, True)
            return 1
        elif start + y + delta > len(DATA):
            start = len(DATA) - curses.LINES + 1
            reprint()
            y = curses.LINES - 1
            stdscr.move(y, 0)
            reattr(y, True)
            return y

        if 0 < y + delta < curses.LINES:
            y = y + delta
        elif y + delta < 1:
            start += y + delta - 1
            reprint()
            y = 1
        else:
            start += y + delta - curses.LINES + 1
            reprint()
            y = curses.LINES - 1
        stdscr.move(y, 0)
        reattr(y, True)
        stdscr.refresh()
        return y

    # Init color pairs
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
    curses.curs_set(False)

    # Print initial content
    stdscr.clear()
    start = 0
    reprint()
    y = 1
    stdscr.move(y, 0)
    reattr(y, True)

    while True:
        c = stdscr.getch()
        if c in (ord('j'), curses.KEY_DOWN):
            y = move(y, 1)
        elif c in (ord('k'), curses.KEY_UP):
            y = move(y, -1)
        elif c == curses.KEY_PPAGE:
            y = move(y, -curses.LINES)
        elif c == curses.KEY_NPAGE:
            y = move(y, curses.LINES)
        elif c == curses.KEY_HOME:
            y = move(y, -len(DATA))
        elif c == curses.KEY_END:
            y = move(y, len(DATA))
        elif c == ord(' '):
            DATA[start + y - 1]['selected'] = not DATA[start + y - 1]['selected']
            y = move(y, 1)
        elif c == ord('c'):     # temporally behavior
            mpv_wrapper('https://youtu.be/' + DATA[start + y - 1]['url'])
        elif c in (ord('q'), 27):   # 27 is Escape key
            break
        stdscr.refresh()


parser = ArgumentParser(description="console/curses online media player")
parser.add_argument('-j', '--json-playlist', required=False,
                    help='path to playlist in JSON format')
args = parser.parse_args()
with open(args.json_playlist) as f:
    DATA = json.load(f)
for i in DATA:
    i['selected'] = False

curses.wrapper(interface)
