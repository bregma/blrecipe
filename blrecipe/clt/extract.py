"""
Submodule to extract icons from the assts texture atlas
"""

import os
import msgpack
from PIL import Image, ImageFilter


def add_parser(subparsers):
    """
    Add the CLI argument parser for this submodule
    """
    parser = subparsers.add_parser('extract',
                                   help='extract icons from the texture atlas')
    parser.add_argument('assetdir',
                        help='root folder of the game assets')
    parser.set_defaults(func=_extract_icons)


def _msgpack_transform(keys, data):
    """
    Transform the msgpack data into useful Python data.
    """
    if isinstance(data, bytes):
        return data.decode('utf-8')
    elif isinstance(data, list):
        return [_msgpack_transform(keys, element) for element in data]
    elif isinstance(data, dict):
        return {keys[int(key)].decode('utf-8'): _msgpack_transform(keys, value)
                for key, value in data.items()}
    return data


def _get_atlas_index(filename):
    """
    Load the texture atlas index
    """
    with open(filename, 'rb') as index_file:
        unpacked = msgpack.unpack(index_file)
        return  _msgpack_transform(unpacked[1], unpacked[0])


class Extractor(object):  # pylint: disable=too-few-public-methods
    """
    Wrap the stateful extraction of icons
    """

    def __init__(self, args):
        atlas_name = os.path.join(args.assetdir, 'gui', 'atlas.png')
        index_name = os.path.join(args.assetdir, 'gui', 'atlas.msgpack')
        self._args = args
        self._atlas = Image.open(atlas_name)
        self._atlas_index = _get_atlas_index(index_name)

    def extract(self):
        """
        Extract all icons fro the etxture atlas.
        """
        for entry in self._atlas_index['sprites']:
            if '/icons/' in entry['name']:
                self._extract_icon(entry)

    def _extract_icon(self, entry, outdir='icons'):
        """
        Extract a single icon fro the texture atlas.
        """
        path = os.path.split(entry['name'])
        filename = path[1]
        category = os.path.split(path[0])[1]
        print(filename)

        uvs = entry['uvs']
        try:
            channel = entry['channel']
        except KeyError:
            channel = 0
        try:
            scale = entry['scale']
        except KeyError:
            scale = 1.0

        # Extract the icon image from the texture atlas.
        uvs[2] += uvs[0]
        uvs[3] += uvs[1]
        icon_img = self._atlas.crop(tuple(uvs))

        # Extract the indicated Luminance channel: the atlas compounds
        # grey-scale icons on all 3 RGB channels.
        icon_img = icon_img.getchannel(channel)

        # Sharpen
        icon_img = icon_img.filter(ImageFilter.UnsharpMask(radius=8, percent=96, threshold=48))

        # Add an alpha channel and make the background transparent.
        icon_img = icon_img.convert('LA')
        new_icon = []
        for item in icon_img.getdata():
            new_icon.append((item[0], item[0]))
        icon_img.putdata(new_icon, scale)

        # save the icon to a file
        out_path = os.path.join(outdir, category)
        os.makedirs(out_path, exist_ok=True)
        icon_img.save(os.path.join(out_path, filename))


def _extract_icons(args):
    """
    Perform icon extraction
    """
    extractor = Extractor(args)
    extractor.extract()


