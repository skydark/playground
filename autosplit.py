#!/usr/bin/python2
# -*- coding: utf-8 -*-


from os import path

import Image

from utils import makeSrcDst, imageFilter


def autoSplit(im, threshold=1.0):
    width, height = im.size
    if 1.0 * width / height > threshold:
        split_width = width / 2
        im1 = im.crop((0, 0, split_width, height))
        im2 = im.crop((split_width, 0, width, height))
        return [im1, im2]
    return [im]


def main(source, destination, **options):
    outfmt = options['outfmt']
    threshold = options['threshold']

    for source, destination in makeSrcDst(source, destination,
                                          src_filter=imageFilter):
        im = Image.open(source)
        im.load()
        ims = autoSplit(im, threshold=threshold)
        parts = len(ims)
        for part, im in enumerate(ims, 1):
            directory, basename = path.split(destination)
            root, ext = path.splitext(basename)
            new_root = outfmt.format(root=root, part=part,
                    part_rev=parts+1-part)
            outfile = path.join(directory, new_root + ext)
            im.save(outfile)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                        description='Auto split double page comic pictures')
    parser.add_argument('source', type=str,  # nargs='+',
                        help='input image file/directory')
    parser.add_argument('destination', type=str,
                        help='output image file/directory')
    parser.add_argument('--threshold', type=float, default=1.0,
                        help='if width/height > threshold, split')
    parser.add_argument('--outfmt', type=str, default='{root}_{part}',
                        help='output format')

    args = parser.parse_args()
    main(**vars(args))
