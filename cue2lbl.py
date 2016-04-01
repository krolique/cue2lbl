# -*- coding: utf-8 -*-
"""
    cub2lbl
    -------

    This module converts CUE files into Audacity labels format

"""

import os
import argparse


def get_title(line):
    """ Returns the track title """

    assert line is not None
    # the format of  line should be like this:
    #   '    TITLE "Some Title"'
    # and we simply can just ignore the first 11 chars, but to be safe lets
    # make this assertion
    assert line[:11] == '    TITLE "'
    # the last char should be a quote, this assertion helps validate this
    # assumption
    assert line[-1] == '"'
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

    assert line is not None
    # each index line for title should begin with this '    INDEX 0'
    assert line[:11] == '    INDEX 0'
    # there could higher-numbered indexes but I haven't seen any in QUE files
    assert line[11] == '0' or line[11] == '1'
    # were not interested int pregap track start time
    if line[11] == '0':
        return
    # making sure we have the right index, which is required
    assert line[11] == '1'

    # expecting the remainder to contain only something that fits the
    # following format dd:dd:dd
    assert line[12:].strip().count(':') == 2

    minutes, seconds, frames = line[12:].strip().split(':')

    # checking every value ensuring its numeric by composition
    assert minutes.isdigit()
    assert seconds.isdigit()
    assert frames.isdigit()

    minutes, seconds, frames = int(minutes), int(seconds), int(frames)

    # doesn't hurt to check the value ranges
    assert minutes >= 0
    assert seconds >= 0 and seconds <= 59
    assert frames >= 0 and frames <= 75

    frames_to_sec = frames / 75

    assert isinstance(frames_to_sec, float)

    frames_to_sec = round(frames_to_sec, 6)

    # terrible hack to find the mantissa part however its fast enough?
    frames_to_sec = str(frames_to_sec).split('.')
    assert len(frames_to_sec) == 2
    assert frames_to_sec[1]

    # we want to cap the number of digits we get back to six. I don't thinks
    # Audacity cares about values after this precision
    frames_to_sec = frames_to_sec[1][:6]

    assert len(frames_to_sec) <= 6

    # padding with zeros to make the output look aligned
    frames_to_sec = frames_to_sec.ljust(6, '0')

    assert len(frames_to_sec) == 6

    return '%d.%s' % (minutes * 60 + seconds, frames_to_sec)


def get_tracks(path_to_file):
    """ Returns tracks """

    if not os.path.isfile(path_to_file):
        raise IOError('the file doesn\'t appear to be a file. yea like may '
                      'be it\'s not a file. who knows try again, may be?')

    # we're going to be doing look-aheads, don't want to peek around with the
    # file access pointer. These files are typically small with tracks into
    # double digits. I think its safe to load the entire file into mem
    data = []
    with open(path_to_file, 'r') as f_pt:
        data = [line[:-1] for line in f_pt]

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


def write_label_file(file_path, over_write_existing=False, root_path=None):
    """ Writes a label.txt file generated from file_path to the QUE file """

    if root_path:
        file_path = os.path.join(root_path, file_path)
    else:
        root_path = os.path.dirname(file_path)

    tracks = get_tracks(path_to_file=file_path)

    labels_file = os.path.join(root_path, 'labels.txt')
    if os.path.isfile(labels_file) and not over_write_existing:
        raise IOError('Can\'t create [%s]. This file already '
                      'exists. Set the overwrite option' % labels_file)
    with open(labels_file, 'w') as f_pt:
        if os.path.isfile(labels_file) and over_write_existing:
            f_pt.truncate()
        for track in tracks[:-1]:
            f_pt.write("%s\n" % track)
        f_pt.write("%s" % tracks[-1])


def write_labels_in_dir(dir_path, over_write_existing=False):
    """ Writes labels files for all the QUE files in the directory and
    subdirectories"""

    if not os.path.isdir(dir_path):
        raise IOError('the directory doesn\'t appear to be a directory. '
                      'yea like may be it\'s not a directory. who knows '
                      'try again, may be?')

    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.lower()[-4:] == '.cue':
                write_label_file(file_path=file,
                                 over_write_existing=over_write_existing,
                                 root_path=root)


if __name__ == "__main__":

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("-d", "--dirpath", help='Path to the directory where'
                        ' QUE files may be found')
    PARSER.add_argument("-f", "--filepath", help='Path to the file where QUE'
                        ' file exists')
    PARSER.add_argument("-o", "--overwrite", help='Enables the converter to '
                        'overwrite existing label.txt files',
                        action='store_true',
                        default=False)

    ARGS = PARSER.parse_args()
    if ARGS.dirpath and ARGS.filepath:
        print('Cant set both -d and -f options at the same time')
    elif ARGS.dirpath:
        try:
            write_labels_in_dir(dir_path=ARGS.dirpath,
                                over_write_existing=ARGS.overwrite)
        except IOError as exception:
            print(exception)
    elif ARGS.filepath:
        try:
            write_label_file(file_path=ARGS.filepath,
                             over_write_existing=ARGS.overwrite)
        except IOError as exception:
            print(exception)
