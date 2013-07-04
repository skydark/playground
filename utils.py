# -*- coding: utf-8 -*-

import os
from glob import glob


IMAGE_EXTS = ('jpg', 'png', 'bmp', 'jpeg')


def imageFilter(source):
    return os.path.splitext(source)[1][1:].lower() in IMAGE_EXTS


def makeSrcDst(source, destination, src_filter=None, ignore_dst=None):
    def make_destination(source):
        source_name = os.path.basename(source)
        return os.path.join(destination, source_name)

    if os.path.isfile(source):
        sources = [source]
        if destination.endswith(os.sep):
            if os.path.isdir(destination):
                destinations = [make_destination(source)]
            else:
                raise IOError('Output directory not found!')
        else:
            destinations = [destination]
    elif os.path.isdir(source):
        sources = [os.path.join(source, f) for f in os.listdir(source)]
        sources = filter(os.path.isfile, sources)
        sources = filter(src_filter, sources)
        if destination == ignore_dst:
            destinations = [destination] * len(sources)
        else:
            if os.path.isfile(destination):
                raise OSError('Destination should be a directory!')
            try:
                os.mkdir(destination)
            except OSError:  # FileExistsError:
                pass
            destinations = [make_destination(source) for source in sources]
    else:
        raise IOError('Input file not found!')

    return zip(sources, destinations)
