#!/usr/bin/python2
# -*- coding: utf-8 -*-


from collections import defaultdict

import Image
import ImageChops
import ImageFilter

from utils import makeSrcDst, imageFilter


def getBackgroundColor(im, edge=None):
    if edge is None:
        edge = 5
    width, height = im.size
    left   = im.crop((0, edge, edge, height - edge))
    right  = im.crop((width - edge, edge, width, height - edge))
    top    = im.crop((0, 0, width, edge))
    bottom = im.crop((0, height - edge, width, height))

    colors = defaultdict(lambda: 0)
    for img in (left, right, top, bottom):
        w, h = img.size
        for i in range(w):
            for j in range(h):
                c = img.getpixel((i, j))
                colors[c] += 1

    colors_reversed = [(count, color) for (color, count) in colors.items()]
    background_color = max(colors_reversed)[1]
    return background_color


def clearPixels(im, width_range, height_range, c=0):
    for i in range(*width_range):
        for j in range(*height_range):
            im.putpixel((i, j), c)
    return im


def getbbox(im, max_error=0.01, threshold=15, suppress=5, max_edge_per=0.1):
    im = im.filter(ImageFilter.GaussianBlur())
    im = im.filter(ImageFilter.FIND_EDGES)
    im = im.filter(ImageFilter.MedianFilter(3))
    # im.show()

    width, height = im.size
    continue_failed = 0
    edges = []
    left_edge = int(height * max_edge_per)
    right_edge = height - 1 - int(height * max_edge_per)
    top_edge = int(width * max_edge_per)
    bottom_edge = width - 1 - int(width * max_edge_per)
    for start, end, step in (
            (0, left_edge, 1),
            (height - 1, right_edge, -1),
            ):
        continue_failed = 0
        for i in range(start, end, step):
            count = 0
            for j in range(width):
                c = im.getpixel((j, i))
                if c <= threshold:
                    count += 1
            error = 1.0 - 1.0 * count / width
            if error >= max_error:
                if continue_failed >= suppress:
                    break
                continue_failed += 1
            else:
                continue_failed = 0
        t = i - continue_failed * step
        edges.append(t)
        im = clearPixels(im, (0, width), (start, t, step))
    for start, end, step in (
            (0, top_edge, 1),
            (width - 1, bottom_edge, -1),
            ):
        continue_failed = 0
        for i in range(start, end, step):
            count = 0
            for j in range(height):
                c = im.getpixel((i, j))
                if c <= threshold:
                    count += 1
            error = 1.0 - 1.0 * count / height
            if error >= max_error:
                if continue_failed >= suppress:
                    break
                continue_failed += 1
            else:
                continue_failed = 0
        t = i - continue_failed * step
        edges.append(t)
        im = clearPixels(im, (start, t, step), (0, height))
    top, bottom, left, right = edges
    return (left, top, right, bottom)


def autoCrop(image, **options):
    gray = image.convert('L')
    background_color = getBackgroundColor(gray, options.get('edge', None))
    bg = Image.new("L", gray.size, background_color)
    diff = ImageChops.difference(gray, bg)
    bbox = getbbox(diff, **options)
    # print(image.size, bbox)
    image = image.crop(bbox)
    return image


def main(source, destination, **options):
    show = options['show'] or destination == '-'
    edge = options['edge']
    del options['show'], options['edge']

    for source, destination in makeSrcDst(source, destination,
                                          src_filter=imageFilter,
                                          ignore_dst='-'):
        im = Image.open(source)
        im.load()
        im = autoCrop(im, **options)

        if show:
            im.show()
        if destination != '-':
            im.save(destination)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                        description='Auto detect white space and crop image')
    parser.add_argument('source', type=str,  # nargs='+',
                        help='input image file/directory')
    parser.add_argument('destination', type=str,
                        help='output image file/directory')
    parser.add_argument('--edge', type=int, default=5,
                        help='get background color from edge')
    parser.add_argument('--threshold', type=int, default=15,
                        help='color diff threshold')
    parser.add_argument('--suppress', type=int, default=5,
                        help='error suppress counter')
    parser.add_argument('--max-error', type=float, default=0.01,
                        help='error detect sensitivity')
    parser.add_argument('--max-edge-per', type=float, default=0.1,
                        help='max ratio for page cut')
    parser.add_argument('-s', '--show', action='store_true',
                        help='show output')

    args = parser.parse_args()
    main(**vars(args))
