# -*- coding: utf-8 -*-
"""
    cub2lbl
    -------

    This module converts CUE files into Audacity labels format

"""


def get_title(line):
    """ Returns the title track metadata """
    # TITLE, PERFORMER and SONGWRITER
    # CD-Text metadata; applies to the whole disc or a specific track,
    # depending on the context
    assert(line is not None)
    # the format of '    TITLE "Some Title"' and we simply can just
    # ignore the first 11 chars, but to be safe lets make this
    # assertion
    assert(line[:11] == '    TITLE "')
    # the last char should be a quote, this assertion helps validate this
    # assumption
    assert(line[-1] == '"')
    return line[11:-1].strip()


def get_track_start(line):
    """ Return the track start time

    Indicates an index (position) within the current FILE. The position
    is specified in mm:ss:ff (minute-second-frame) format. There are 75
    such frames per second of audio. In the context of cue sheets,
    "frames" refer to CD sectors, despite a different, lower-level
    structure in CDs also being known as frames. INDEX 01 is required
    and denotes the start of the track, while INDEX 00 is optional and
    denotes the pregap. The pregap of Track 1 is used for Hidden Track
    One Audio (HTOA). Optional higher-numbered indexes (02 through 99)
    are also allowed.

    """

    assert(line is not None)
    # each index line should begin with this '    INDEX 0'
    assert(line[:11] == '    INDEX 0')
    # there are 
    assert(line[11] == '0' or line[11] == '1')
    # were not interested int pregap track start time
    if line[11] == '0':
        return
    # making sure we have the right index, which is required
    assert(line[11] == '1')

    minutes, seconds, frames = line[12:].strip().split(':')
    frames_to_sec = str(int(frames) / 75).split('.')[1][:6].ljust(6, '0')
    return '%d.%s' % (int(minutes) * 60 + int(seconds), frames_to_sec)


def get_tracks(path_to_file):
    """ Returns tracks """

    data = [line[:-1] for line in open(path_to_file, 'r')]
    tracks = []
    for idx in range(len(data)):
        # Each audio track section begins with this line
        if 'TRACK' in data[idx]:
            title = None
            track_start = None
            for t_idx in range(1, 5):
                if all([title, track_start]):
                    break
                try:
                    next_line = data[idx + t_idx]
                    if 'TRACK' in next_line:
                        break
                    if 'TITLE' in next_line:
                        title = get_title(next_line)
                    if 'INDEX' in next_line:
                        track_start = get_track_start(next_line)
                except IndexError:
                    break
            tracks.append('%s %s %s' % (track_start.ljust(11), 
                    track_start.ljust(11), title))

    return tracks


for track in get_tracks(path_to_file=file_path):
    print(track)
