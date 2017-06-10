# ie.py - Omni Media Player infomation extractor
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
from time import gmtime, sleep, strftime

from youtube_dl import YoutubeDL
from mpv import MPV

DEFAULT_ENTRY = {'filename': '', 'title': '', 'duration': '00:00:00',
                 'error': False, 'playing': False, 'selected': False}
YTDL_OPTS = {'quiet': True, 'default_search': 'ytsearch',
             'extract_flat': 'in_playlist'}


def json_extract_info(filename):
    """Return list of entries extracted from a file using json. If an
    error occur during the extraction, return None.
    """
    try:
        with open(filename) as f: raw_info, info = json.load(f), []
        for i in raw_info:
            e = DEFAULT_ENTRY.copy()
            for k in e:
                if k in i and isinstance(i[k], type(e[k])): e[k] = i[k]
            info.append(e)
    except:
        return None
    else:
        return info


def mpv_extract_info(filename):
    """Return list of entries extracted from a path or URL using mpv. If
    an error occur during the extraction, return None.
    """
    mp = MPV(ytdl=True, vid=False)
    mp.play(filename)
    while mp.duration is None:
        sleep(0.25)
        if mp.playback_abort: return None
    info = {'filename': filename, 'title': mp.media_title.decode(),
            'duration': mp.osd.duration, 'error': False, 'playing': False,
            'selected': False}
    mp.quit()
    return [info]


def ytdl_extract_info(filename):
    """Return list of entries extracted from a path or URL using
    youtube-dl. If an error occur during the extraction, return None.
    """
    with YoutubeDL(YTDL_OPTS) as ytdl:
        try:
            raw_info = ytdl.extract_info(filename, download=False)
        except:
            return None
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
                try:
                    i['title'] = ytdl.extract_info(i['filename'],
                                                   download=False)['title']
                except:
                    return None
            if 'duration' not in i:
                i['duration'] = '00:00:00'
            elif isinstance(i['duration'], int):
                i['duration'] = strftime('%H:%M:%S', gmtime(i['duration']))
            for k in 'error', 'playing', 'selected': i.setdefault(k, False)
            for k in i.copy():
                if k not in DEFAULT_ENTRY: i.pop(k)
    return info


def extract_info(filename, extractor='youtube-dl'):
    """Return list of entries extracted from a path or URL using
    specified extractor. If an error occur during the extraction,
    return None.

    The extractor could be either 'json', 'mpv' or 'youtube-dl' and
    fallback to 'youtube-dl'.
    """
    if isfile(expanduser(expandvars(filename))):
        filename = abspath(expanduser(expandvars(filename)))
    if extractor == 'json':
        return json_extract_info(filename)
    elif extractor == 'mpv':
        return mpv_extract_info(filename)
    else:
        return ytdl_extract_info(filename)
