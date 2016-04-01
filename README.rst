cue2lbl
-------
Simple way to generate Audacity label files from CUE files

Setup
-----

This module requires Python 3. Yep. Like totally stop using Python 2.


Usage
-----
The usage is very simple. Either your know the path to the QUE file or you
would like to convert an entire directory structure full of QUE files

Case #1 - you know the file location ::

    > python cue2lbl.py -f /home/user/music/album/output.que -o


Case #2 - you would like to convert a while bunch of QUE files::

    > python cue2lbl.py -d /home/user/music/albums -o


